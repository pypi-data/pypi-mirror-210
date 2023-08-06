""" Pedestals controller

All pedestals management happens here.

Background:

    Pedestals are used to compensate for imperfections in the chip manufacturing
    process, by capturing enough events from the storage array it's possible to
    statistically rule out data originating from these imperfections rather
    than the real world event.

Instructions:

    This controller can run as a one-shot:
    PedestalsController(board, daq).generate_pedestals()

    or persistent:
    ped_ctrl = PedestalsController(board, daq)
    ped_ctrl.generate_pedestals()

.. todo::
    - _capture_data_for_pedestals currently works different for SiREAD, should be uniform.
    - Need a way to track progress and run non-blocking

"""
import copy
import gzip
import logging
import os
import pickle
import time
from collections import deque
from typing import Iterable

import deprecation
import numpy as np

from naludaq.communication import control_registers, digital_registers
from naludaq.controllers import get_board_controller, get_readout_controller
from naludaq.daq import get_daq
from naludaq.helpers.exceptions import (
    NotAValidEvent,
    OperationCanceledError,
    PedestalsDataCaptureError,
)
from naludaq.io import io_manager
from naludaq.tools.metadata import Metadata

LOGGER = logging.getLogger(
    "naludaq.pedestals_controller"
)  # pylint: disable=invalid-name
DigitalRegisters = digital_registers.DigitalRegisters
ControlRegisters = control_registers.ControlRegisters


class PedestalsController:
    """Pedestals controller manages the pedestals generation.

    The pedestals are used to reduce noise originating from the chip itself.
    By capturing data from the board it's possible to use the mean value of x events to
    generate an average error for every sample. Since this average is
    an effect of the imperfections in the chip, subtracting the average counteracts
    the effect of the imperfections.

    The average is improving with 1/sqrt(n).

    This controller relies on an external data acquisiton capturing data to the
    .pedstore buffer it also relies on a board with an active connection to
    communicate with the hardware.

    The pedestals can then be used by the parser to remove the noise.

    Args:
        board:
        num_captures (int): Number of datapoints per sample, used for averaging the values.
        num_warmup_events (int): Number of initial events to discard. Helps the board
            settle and excludes events that may skew the pedestals.
        channels (list[int]): list of channels to generate pedestals for. Any channels excluded
            will result as `np.nan` in the generated pedestals.

    Attributes:
        num_captures: How many datapoints/samplepoint used to calculate the average.

    Raises:
        NotImplementedError if the given board does not support pedestals.
    """

    def __init__(
        self, board, num_captures: int = 10, num_warmup_events: int = 10, channels=None
    ):

        self._board = None
        self.board = board
        # The type of daq used depends on the connection type
        self._daq = get_daq(self.board, parsed=True)

        self.pedestals = dict()
        self.block_buffer = deque()  # Can be used for progress check
        self.validated_data = deque()  # Can be used for progress check
        self._warmup_data = deque()  # each element is a block
        self.validated_blocks = []

        self.channels = channels or list(range(self.board.channels))
        self.num_captures = num_captures
        self.num_warmup_events = num_warmup_events
        self._store_warmup_events = False

        self.margin = 1.1
        self.sleeptime = sleep_calc(self.board, len(self._channels))
        self._progress = []
        self._cancel = False

    @property
    def board(self):
        """Get/set board for pedestals capture.

        Raises:
            NotImplementedError if the given board does not support pedestals.
        """
        return self._board

    @board.setter
    def board(self, board):
        if not board.is_feature_enabled("pedestals"):
            raise NotImplementedError(
                f'Board "{board.model}" does not have support for pedestals.'
            )
        self._board = board

    @property
    def progress(self):
        """Get/Set the progress message queue.

        This is a hook the read the progress if running threads.
        """
        return self._progress

    @progress.setter
    def progress(self, value):
        if not hasattr(value, "append"):
            raise TypeError(
                "Progress updates are stored in an object with an 'append' method"
            )
        self._progress = value

    @property
    def channels(self) -> "list[int]":
        """Get/set the channels that will be read out. Any channels not enabled will result
        in NANs for that channel.
        """
        return self._channels

    @channels.setter
    def channels(self, channels: "list[int]"):
        if not isinstance(channels, Iterable):
            raise TypeError("Channels must be a list[int]")
        if len(channels) == 0:
            raise ValueError("At least one channel must be given")
        if any(not isinstance(c, int) for c in channels):
            raise TypeError("Channels must be a list[int]")
        if any(not 0 <= c < self.board.channels for c in channels):
            raise ValueError("One or more channel numbers are out of bounds")
        self._channels = list(set(channels))

        # minimum sleep time changes with number of channels
        self.sleeptime = sleep_calc(self.board, len(self._channels))

    @property
    def metadata(self) -> Metadata:
        """Get a proxy object to use for accessing pedestals metadata."""
        return Metadata(self.board.pedestals)

    def cancel(self):
        """Cancels the pedestals generation as soon as possible.
        No pedestals are generated, and the board is restored to
        its previous state.

        Can only be called from a separate thread.
        """
        self._cancel = True

    def generate_pedestals(self):
        """Generates pedestals and stores them in the board.pedestals.

        Pedestals stored on the board, they will be used on the next acquisition.

        If canceled, the board is set back to its previous state, and no pedestals
        are generated.
        """
        self._cancel = False
        old_peds = getattr(self.board, "pedestals", {})
        self.reset_pedestals()
        self._reset_buffers()
        self._store_board_metadata()
        backup = self._backup_settings()

        self._generate_pedestals_metadata_pre()
        try:
            self._capture_data_for_pedestals()
        except (Exception, KeyboardInterrupt):
            self.cancel()
            raise
        finally:
            self._clean_up(backup)
            if self._cancel:
                self.board.pedestals = old_peds
        if self._cancel:
            return
        self._generate_pedestals_metadata_post()
        self._generate_pedestals_data()
        self._generate_pedestals_from_data()
        _update_progress(self.progress, 100, "Pedestals generated")

    def reset_pedestals(self):
        """Remove the current pedestal data.

        Replaces the pedestals with a set of blank pedestals. All values set
        to zero with the shape set from board params.
        """
        self.board.pedestals = dict()
        self.board.pedestals["data"] = self._set_pedestals_to_zero()
        self._reset_pedestals_data()

    def _set_pedestals_to_zero(self):
        """Set pedestals to zero."""
        output = np.zeros(
            shape=(
                self.board.params["channels"],
                self.board.params["windows"],
                self.board.params["samples"],
            )
        )
        return output

    def _reset_pedestals_data(self, num_captures=None):
        """Reset all pedestals data to an empty shape.

        The shape of the empty pedestals.data is:
        [channels][windows][samples][num_captures]

        Args:
            num_captures (int): Override number of captures for pedestals generation.
                Leave as None is unsure.
        """
        if self.board.pedestals is None:
            self.board.pedestals = dict()
        self.board.pedestals["rawdata"] = self._set_pedestals_raw_to_zero(num_captures)

    def _set_pedestals_raw_to_zero(self, num_captures):
        """Build the structure for raw pedestals data."""
        if num_captures is None:
            num_captures = self.num_captures

        output = np.empty(
            shape=(
                self.board.params["channels"],
                self.board.params["windows"],
                self.board.params["samples"],
                num_captures,
            )
        )
        output[:] = np.NaN

        return output

    def _reset_buffers(self):
        self.block_buffer = deque()
        self.validated_data = deque()
        self.validated_blocks = []
        self._switch_daq_buffer()

    def _clean_up(self, backup):
        """Restores backup settings and stops board and daq readout/capture"""
        self._restore_backup_settings(backup)
        get_board_controller(self.board).stop_readout()
        self._daq.stop_capture()

    def _backup_settings(self) -> dict:
        """Backup settings that might get overwritten to a dict.

        Returns:
            dict with the backup settings:
                'readout_channels',
                'control_registers',
                'digital_registers'
        """
        backup = {
            "readout_channels": get_readout_controller(
                self.board
            ).get_readout_channels(),
            "control_registers": copy.deepcopy(
                self.board.registers.get("control_registers", {})
            ),
            "digital_registers": copy.deepcopy(
                self.board.registers.get("digital_registers", {})
            ),
        }

        return backup

    def _capture_data_for_pedestals(
        self,
        num_captures=None,
        num_warmup_events=None,
    ):
        """Read the data for pedestals generation.

        The data will be captured in blocks, each block will be a fixed set of window numbers.

        Reads `num_captures` samples from each block to average the data.

        The warmup events is always capturing warmup events BEFORE real data.
        The logic will throw away the warmup before transfering validating events.
        in the capture buffer each block will store the data:
         `[warmup_events..., pedestalsdata...]`
        the events in the left will be popped before validation.

        Args:
            num_captures (int): number of events per block
            num_warmup_events (int): number of warmup events to readout. These events
                are not included in the pedestals data.
        """
        board = self.board
        params = board.params

        LOGGER.debug(
            "Board is %s with block: %s", params["model"], params["pedestals_blocks"]
        )
        total_windows = params["windows"]
        block_size = params["pedestals_blocks"]

        # Validation in case of pedestals_blocks typo
        block_size = min(max(block_size, 1), total_windows)

        # Reset readoutchannels to all
        rc = get_readout_controller(board)
        try:
            rc.set_readout_channels(self._channels)
            rc.set_read_window(write_after_trig=total_windows)
            rc.set_read_window(windows=block_size)
        except Exception as e:
            LOGGER.debug("Setting the windows failed due to %s", e)

        num_blocks = self._calculate_number_blocks(block_size, total_windows)

        # Extra code for status #############################################
        min_value = 0
        max_value = 80
        step_value = (max_value - min_value) / num_blocks
        #####################################################################
        LOGGER.debug("Capturing data for pedestals")

        # This will break the child threads and stop capture in cmd-line and notebooks.
        for block in range(num_blocks):
            try:
                prog = min(min_value + step_value * block, max_value)
                _update_progress(
                    self.progress, prog, f"Capturing block: {block+1}/{num_blocks}"
                )

                LOGGER.debug("Block %s/%s", block, num_blocks)

                # Capture validated data for one block into self.validated_data
                if not self._capture_block(
                    block, block_size, num_captures, num_warmup_events
                ):
                    raise PedestalsDataCaptureError(
                        "Failed to validate the return data"
                    )

                # Transfer into validated_blocks, used to generate peds raw data
                self.validated_blocks.append(self.validated_data)

                if self._cancel:
                    break
            except KeyboardInterrupt:
                LOGGER.info("Caught keyboard interrupt, stopping capture children")
                raise KeyboardInterrupt

    def _calculate_number_blocks(self, block_size: int, windows: int) -> int:
        """Calculates number of blocks to use with a certain block_size.

        If blocksize doesn't divide evenly with number of windows, then add one more
        block to capture data the rest.

        Args:
            block_size(int): Amount of windows in a block.
            windows(int): Amount of windows of the hardware.

        Returns:
            Number of blocks as an integer.
        """
        num_blocks = windows // block_size + (windows % block_size > 0)
        return num_blocks

    def _switch_daq_buffer(self):
        """Set the daqs output buffer to the pedestals controllers storage.

        Tell the daq pipeline to store the events for the pedestals in
        a separate storage for the pedestals.
        """
        self._daq.output_buffer = self.block_buffer

    def _capture_block(self, block, block_size, num_captures, num_warmup_events=None):
        """Captures a single block, only keeping validated events.

        Args:
            block (int): the block index (0 to windows / block count - 1)
            block_size (int): number of windows per block
            num_captures (int): number of captures that contribute to pedestals data.
            num_warmup_events (int): number of events to readout before capturing pedestals
                data. Warmup events are not used to generate pedestals.

        Raises:
            TimeoutError if the data could not be read back.

        Returns:
            True if successful, or False otherwise.
        """
        # Readout settings
        num_captures = num_captures or self.num_captures
        num_warmup_events = num_warmup_events or self.num_warmup_events
        total_captures = num_captures + num_warmup_events
        readout_settings = {
            "trig": "i",  # Starts an immediate readout.
            "lb": "f",
            "acq": "ped",
            "ped": "zero",
            "readoutEn": True,
            "singleEv": True,
        }

        self.block_buffer = deque(maxlen=total_captures)
        self.validated_data = deque(maxlen=num_captures)
        self._daq.output_buffer = self.block_buffer
        bc = get_board_controller(self.board)
        rc = get_readout_controller(self.board)
        rc.set_read_window(lookback=block * block_size)

        reset_count = 0
        t_count = 0
        timeout = 10
        needed_amount = total_captures
        while len(self.validated_data) < num_captures:
            if needed_amount <= 0 or self._cancel:
                break

            rc.number_events_to_read(needed_amount)

            self._daq.start_capture()
            bc.start_readout(**readout_settings)
            try:
                finished = self._wait_for_data(self.block_buffer, needed_amount)

                if not finished:
                    if reset_count >= timeout:
                        raise TimeoutError(
                            "Something wrong with setup/hardware, reset 5 times."
                        )
                    LOGGER.debug("data capture failed, restarting")
                    reset_count += 1
                    self.margin = increase_margin(self.margin)
                    self.sleeptime = sleep_calc(self.board, self.margin)

                LOGGER.debug("Data capture finished, stopping")
            finally:
                self._daq.stop_capture()
                bc.stop_readout()
            # self._daq.stop_workers()
            LOGGER.debug("Only keep validated events, need: %s", needed_amount)
            expected_block = self._calculate_expected_block(block, block_size)
            all_validated = False
            if (
                len(self.block_buffer) > num_warmup_events
            ):  # If the amount captured is less than warmup, save none
                all_validated = self._only_keep_validated_events(
                    self.block_buffer,
                    self.validated_data,
                    self._warmup_data if self._store_warmup_events else None,
                    expected_block,
                    num_captures,
                    num_warmup_events,
                )

            if all_validated is True:
                return True
            if t_count > timeout:
                return False
            t_count += 1

            needed_amount = (
                num_warmup_events
                + (num_captures - len(self.validated_data))
                - len(self.block_buffer)
            )

        return True

    def _wait_for_data(self, output_buffer, desired_amount):
        """Wait for the desired amount of data to arrive.

        Returns in these cases:
        - if desired amout is reached
        - if no data is received
        - if too much data is received

        Args:
            output_buffer (deque): storage for data we wait for.
            desired_amount(int): The amount of events we wait for.

        Returns:
            True if the correct amount of data is captured, else False
        """
        result = True
        prev_amount = -1
        # wait for readout to finish
        while len(output_buffer) != prev_amount:
            stime = self.sleeptime * (desired_amount - len(output_buffer))
            if output_buffer:
                prev_amount = len(output_buffer)
            try:  # If output_buffer is larger than desired, stime < 0.
                time.sleep(stime)
            except ValueError:
                pass
            if len(output_buffer) > desired_amount:
                break

        if len(output_buffer) == 0:
            result = False

        return result

    def _only_keep_validated_events(
        self,
        to_validate: deque,
        validated: deque,
        warmup_output: deque,
        expected_block: list,
        expected_amount: int,
        warmup_amount: int,
    ) -> bool:
        """Loop through captured events and only keep validated.

        Args:
            to_validate(deque): events waiting to be validated
            validated(deque): events validated
            expected_block(list): a list of expected window numbers
            expected_amount(int): the amount of events needed to pass.
            warmup_events(int): amount of warmup events before real data.

        Returns:
            True if the expected amount is validated. False if timeout.
        """
        LOGGER.debug("Only keeping validated events.")
        for _ in range(warmup_amount):
            try:
                _ = to_validate.popleft()
            except IndexError:
                return False

        while to_validate and len(validated) != expected_amount:
            try:
                event = to_validate.pop()  # pop from right discards warmup events
            except IndexError:
                continue

            try:
                if self._validate_event(event, expected_block):
                    validated.append(event)
                else:
                    LOGGER.debug("Event not validated")
            except NotAValidEvent as error_msg:
                LOGGER.warning(error_msg)
                LOGGER.debug("Event not validated")

        if len(validated) == expected_amount:
            if warmup_output is not None:
                warmup_output.append(to_validate)
            return True
        return False

    def _validate_event(self, event, expected_block):
        """Returns true if the window labels matches the expected_block.

        The validation matches the received window_labels with the expected
        window labels to make sure the block contains only data from that
        block. The firmware buffer sometimes contains more data from a previous block
        this makes sure it doesn't enter the next block buffer.

        Args:
            event(dict): event to validate
            expected_block(list): a list of expected window numbers

        Returns:
            True if validated, False if the events windows doesn't match expected.

        Raises:
            NotAValidEvent if the event doesn't have a window_labels key.
        """
        test_channel = self._channels[0]
        try:
            if np.all(event["window_labels"][test_channel] == expected_block):
                return True
        except Exception as error_msg:
            raise NotAValidEvent(f"Event validataion failed due to: {error_msg}")
        else:
            # LOGGER.debug(
            print(
                "Expected: %s != returned: %s",
                expected_block,
                event["window_labels"][test_channel],
            )
            return False

    def _calculate_expected_block(self, block, block_size):
        """If a board doesn't have a junk register, there will be more expected blocks.

        Args:
            block(int): Current block number.
            block_size(int): Number of windows captured per block.

        Returns:
            List of expected window numbers.
        """
        expected_block = np.arange(block * block_size, (block + 1) * block_size) % (
            self.board.params["windows"]
        )

        return expected_block

    def _restore_backup_settings(self, backup_settings):
        """Restore all backuped settings to the board.

        Returns:
            True if settings have been restored, False if no old settings were found.
        """
        if not backup_settings:
            return

        get_readout_controller(self.board).set_readout_channels(
            backup_settings["readout_channels"]
        )

        # Restore backup
        for register in ["control_registers", "digital_registers"]:
            self.board.registers[register] = backup_settings.get(register, {})
        DigitalRegisters(self.board).write_all()
        ControlRegisters(self.board).write_all()

    # Metadata #######################################################################################
    def _generate_pedestals_metadata_pre(self):
        """Adds some metadata to the pedestals dict. Called immediately
        before the pedestals data will be captured.
        """
        self._store_board_metadata()
        self._store_sensor_readings()

    def _generate_pedestals_metadata_post(self):
        """Adds some metadata to the pedestals dict. Called immediately
        after the pedestals data has been captured.
        """
        self._store_sensor_readings()
        self._store_time_metadata()

    def _store_board_metadata(self):
        """Store board params/registers into pedestals metadata"""
        self.metadata.set_configuration(self.board)

    def _store_sensor_readings(self):
        """Store sensor readings into pedestals metadata"""
        LOGGER.debug("Storing sensor metadata")
        self.metadata.store_sensor_readings(self.board)

    def _store_time_metadata(self):
        """Store event times into pedestals metadata"""
        LOGGER.debug("Storing time metadata")
        md = self.metadata
        for block in self.validated_blocks:
            md.store_event_times(block)

    # Process data ###################################################################################
    def _generate_pedestals_from_data(self):
        """Generate pedestals data and average it.

        Takes the generated pedestals data and generates the actual pedestals.
        The pedestals are stored in the controller and can be retreived with
        get_pedestals().

        """
        rawdata = self.board.pedestals["rawdata"]
        output = np.nanmean(rawdata, axis=3)
        self.board.pedestals["data"] = output
        if self._store_warmup_events:
            LOGGER.debug("Warmup storage flag set, storing in pedestals")
            self.board.pedestals["warmup_data"] = self._warmup_data

    def _generate_pedestals_data(self, num_captures=None):
        """Generates the pedestals data from captured data.

        Uses captured events in the pedestals_raw_data deque
        to generate the data.

        Args:
            nCaptures (int): Number of captures, default 10
            blocksize (int): size of blocks, default 16
        """

        if num_captures is None:
            num_captures = self.num_captures

        block_size = self.board.params["pedestals_blocks"]

        self._reset_pedestals_data(num_captures)

        LOGGER.debug(
            "Generating pedestals from %s samples with blocksize: %s",
            num_captures,
            block_size,
        )

        return self._create_raw_pedestals_data(block_size, num_captures)

    def _create_raw_pedestals_data(self, block_size, num_captures):
        """Move data to board.pedestals after validating.

        Since data already is prevalidated this is just a logic check,

        Args:
            block_size(int): windows per block
            num_captures(int): amount of events averaged.
        """
        self.board
        num_blocks = self._calculate_number_blocks(
            block_size, self.board.params["windows"]
        )
        assert num_blocks == len(self.validated_blocks)

        # STATUS UPDATES ####################################
        min_value = 80
        max_value = 95
        step_value = (max_value - min_value) / num_blocks
        #####################################################
        for block_idx, block in enumerate(self.validated_blocks):
            LOGGER.info("Capturing block %s/%s", block_idx + 1, num_blocks)
            # Status message ###############################
            _update_progress(
                self.progress,
                min_value + step_value * block_idx,
                f"Processing data: {block_idx+1}/{num_blocks}",
            )
            ###############################################
            for cap, event in enumerate(block):
                for chan in range(self.board.params["channels"]):
                    if chan not in self._channels:
                        continue
                    for window_num in range(block_size):
                        window = window_num + block_idx * block_size

                        # Avoid rolling over and overwrite block 0
                        if block_idx != 0 and (window < block_size):
                            continue
                        # avoid window number rolling over
                        if window >= self.board.params["windows"]:
                            continue

                        for sample in range(self.board.params["samples"]):
                            index = sample + window_num * self.board.params["samples"]
                            data = event["data"][chan][index]
                            self.board.pedestals["rawdata"][chan][window][sample][
                                cap
                            ] = data

        return True

    def _raise_if_canceled(self):
        """Raise an ``OperationCanceledError`` if the cancel flag is set."""
        if self._cancel:
            raise OperationCanceledError("Pedestals generation was canceled.")

    def _increase_sleeptime(self, needed_amount):
        """Increase the sleeptime based on received vs expected.

        Formula is intended to change the margin incrementally without
        causing to much oscillation.
        """
        # inc = (needed_amount / len(self.block_buffer))/2 + 1 settles at 0.45
        # inc = (needed_amount / len(self.block_buffer))/2 fails
        # inc = (needed_amount / len(self.block_buffer)) Oscillates
        block_len = max(len(self.block_buffer), 1)
        inc = (needed_amount / block_len) / 3 + 1  # Settles at 0.38
        self.margin = increase_margin(self.margin, margin_inc=inc, max_margin=10)
        self.sleeptime = sleep_calc(
            self.board, self.margin, channels=len(self._channels)
        )
        LOGGER.debug("Waittime changed to %s", self.sleeptime)

    # Functions to export data
    @staticmethod
    def save_pedestals(pedestals, filename):  # TODO(v.0.1.23): Use IO module.
        """Save the pedestal in binary format for backwards compatibility."""
        if not isinstance(pedestals, dict):
            raise TypeError(f"pedestals must be a dict, got {type(pedestals)}")
        if filename is None:
            raise TypeError("Supplied pathname is NoneType.")
        path, _ = os.path.split(filename)
        if not os.path.isdir(path):
            raise NotADirectoryError(f"Not a valid directory: {path}")

        try:
            sfile = gzip.GzipFile(filename, "w", compresslevel=4)
            pickle.dump(pedestals, sfile, protocol=pickle.HIGHEST_PROTOCOL)
        except IOError as error_msg:
            LOGGER.error("File could not be created. %s", error_msg)
        except pickle.PicklingError as error_msg:
            LOGGER.error("Saving pedestals failed: %s", error_msg)

    def load_pedestals(self, filename):  # TODO(v.0.1.23): Use IO module.
        """Load the pedestal gziped and pickled.

        The pedestals object is loaded to both self.pedestals
        and is returned.

        Args:
            filename: valid filename

        Returns:
            Pedestals data.
        """
        outped = get_pedestals_from_file(filename)
        self.board.pedestals = outped
        return outped

    @deprecation.deprecated(
        deprecated_in="0.1.22",
        details="Use the IO Controller for all csv imports/exports",
    )
    def export_pedestals_csv(self, pedestals, filename):
        """Export all data from the pedestals to CSV.

        Please note this will only export the data, not the information regarding the pedestals.
        This function also assumes filename is in the correct format.
        It will override any existing file.

        Args:
            pedestals (Pedestals): A pedestals object with the pedestals data.
            filename (path): Filename fro the csv file.
        """

        io_manager.IOManager().export_pedestals_csv(self.board, pedestals, filename)


def increase_margin(margin: float, margin_inc: float = 1.5, max_margin: float = 5):
    """Increases the margin, using an exponential standoff"""
    margin *= margin_inc
    margin = min(margin, max_margin)
    return margin


def sleep_calc(board, margin: float = 2.0, channels=None) -> float:
    """Compute the `sleeptime` for the board.

    Using the `board.params` to gather blocksize, baudrate and readout
    parameters compute the minumum sleep time.

    The `margin` can be dynamically altered as a standoff in case the calc
    doesn't match real transfer rate.
    By increasing `margin` it's possible to increase `sleeptime` in case of
    real-world differences between calculated baudrate and real. Or if
    the return data is longer/padded.

    Args:
        board(naludaq.board)
        margin(float): Multiplier to increase sleeptime due to real-world
            scenarios.
        channels (int): number of channels to be read on the board.

    Returns:
        sleeptime in seconds as a float

    """
    if channels is None:
        channels = board.channels
    baudrate = board.connection_info.get("speed", 115200)
    transferrate = baudrate // 8
    windows = board.params.get("pedestals_blocks", 16)
    samples = board.params.get("samples", 64)
    data = windows * channels * samples * margin * 2  # 16-bits per value
    sleeptime = data / transferrate

    return sleeptime


def get_pedestals_from_file(filename):
    """Load the pedestal gzipped and pickled.

    The pedestals object is returned.

    Args:
        filename: valid filename

    Returns:
        Pedestals data.
    """
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"No file found: {filename}")

    try:
        sfile = gzip.GzipFile(filename, "r")
        outped = pickle.load(sfile)
    except EOFError as error_msg:
        LOGGER.error("Reached the end of the file, msg: %s", error_msg)
    except IOError as error_msg:
        LOGGER.error("File could not be loaded. %s", error_msg)
    except pickle.UnpicklingError as error_msg:
        LOGGER.error("Loading pedestals failed: %s", error_msg)
    else:
        if not isinstance(outped, dict):
            raise TypeError(f"Not a valid Pedestals file: {filename}")

        return outped


def _update_progress(receiver, percent: float, message: str):
    """Updates a progress "receiver" with a percent and message.

    The receiver can be a list or deque of (percent, message) tuples,
    or a ProgressDialog (for use with NaluScope).

    Args:
        receiver (list, deque, or ProgressDialog): the receiver of the progress update.
            Can be None to report nothing
        percent (float): the percent completion of the task
        message (str): a description of what is currently taking place
    """
    if receiver is None:
        LOGGER.deubg("%s | %s", percent, message)
        return
    elif isinstance(receiver, (list, deque)):
        receiver.append((percent, message))
    else:
        try:
            receiver.update_status(percent, message)
        except:
            pass
