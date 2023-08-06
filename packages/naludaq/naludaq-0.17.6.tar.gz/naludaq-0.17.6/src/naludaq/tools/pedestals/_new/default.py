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
import itertools
import logging
import os
import pickle
from typing import Iterable, Iterator

import numpy as np

from naludaq.backend.managers import AcquisitionManager
from naludaq.backend.models.acquisition import RemoteAcquisition
from naludaq.board import Board
from naludaq.communication import ControlRegisters, DigitalRegisters
from naludaq.controllers import get_board_controller, get_readout_controller
from naludaq.helpers.exceptions import OperationCanceledError, PedestalsDataCaptureError
from naludaq.helpers.helper_functions import event_transfer_time
from naludaq.tools.metadata import Metadata

LOGGER = logging.getLogger(
    "naludaq.pedestals_controller_new"
)  # pylint: disable=invalid-name


class PedestalsGeneratorNew:
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
        self,
        board: Board,
        num_captures: int = 10,
        num_warmup_events: int = 10,
        channels=None,
    ):
        if not board.is_feature_enabled("pedestals"):
            raise NotImplementedError(
                f'Board "{board.model}" does not have support for pedestals.'
            )
        self._board = board

        self._progress = []
        self._cancel = False

        self._num_captures = num_captures
        self._num_warmup_events = num_warmup_events
        self._block_size = self.board.params["pedestals_blocks"]

        self._margin = 2
        self._sleep_time = 0
        self.channels = channels or range(self.board.channels)  # sets sleep time
        self._debug_raw_events = []

    @property
    def board(self):
        """Get/set board for pedestals capture.

        Raises:
            NotImplementedError if the given board does not support pedestals.
        """
        return self._board

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
    def channels(self) -> list[int]:
        """Get/set the channels that will be read out. Any channels not enabled will result
        in NANs for that channel.
        """
        return self._channels

    @channels.setter
    def channels(self, channels: Iterable[int]):
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
        self._recompute_sleep_time()

    @property
    def block_size(self) -> int:
        """Get/set the number of windows per block"""
        return self._block_size

    @block_size.setter
    def block_size(self, block_size: int):
        self._block_size = block_size

    @property
    def metadata(self) -> Metadata:
        """Get a proxy object to use for accessing pedestals metadata."""
        return Metadata(self.board.pedestals)

    @property
    def raw_events(self) -> list[dict]:
        """List of events used to last generate the pedestals.
        
        These events are parsed, and otherwise not modified in any way.
        They can be used for analysis! 🥳🎉
        """
        return self._debug_raw_events

    def generate_pedestals(self):
        """Generates pedestals and stores them in the board.pedestals.

        Pedestals stored on the board, they will be used on the next acquisition.

        If canceled, the board is set back to its previous state, and no pedestals
        are generated.
        """
        self._cancel = False
        old_pedestals = self.board.pedestals
        self._debug_raw_events = []

        self._update_progress(0, "Saving board state")
        backup = self._backup_settings()

        self.reset_pedestals()
        self._store_board_metadata()

        try:
            self._generate_pedestals_metadata_pre()
            blocks = self._capture_data_for_pedestals()
            self._generate_pedestals_metadata_post()
        except (OperationCanceledError, KeyboardInterrupt):
            self.board.pedestals = old_pedestals
        except:
            self.board.pedestals = old_pedestals
            raise
        else:  # else runs before finally if no error is raised
            self._update_progress(80, "Processing data")
            self._store_raw_data(blocks)
            self._store_averaged_data()
        finally:
            self._update_progress(90, "Restoring board state")
            self._restore_backup_settings(backup)

    def cancel(self):
        """Cancels the pedestals generation as soon as possible.
        No pedestals are generated, and the board is restored to
        its previous state.

        Can only be called from a separate thread.
        """
        self._cancel = True

    def reset_pedestals(self):
        """Remove the current pedestal data.

        Replaces the pedestals with a set of blank pedestals. All values set
        to zero with the shape set from board params.
        """
        self.board.pedestals = self._create_empty_pedestals(self._num_captures)

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

    def _restore_backup_settings(self, backup_settings: dict):
        """Restore all backuped settings to the board.

        Returns:
            True if settings have been restored, False if no old settings were found.
        """
        if not backup_settings:
            return

        channels = backup_settings.get("readout_channels", None)
        if channels is not None:
            get_readout_controller(self.board).set_readout_channels(channels)

        # Restore backup
        for register_space in ["control_registers", "digital_registers"]:
            backup_registers = backup_settings.get(register_space, None)
            if backup_registers is not None:
                self.board.registers[register_space] = backup_registers
        DigitalRegisters(self.board).write_all()
        ControlRegisters(self.board).write_all()

    # ================================================================================
    # Capture
    # ================================================================================
    def _capture_data_for_pedestals(self) -> list[list[dict]]:
        """Capture raw data for pedestals.

        Returns:
            list[list[dict]]: list of data for blocks. Warmup events
                are removed from the output.

        Raises:
            PedestalsDataCaptureError: if pedestals failed to generate.
            OperationCanceledError: if pedestals generation was cancelled.
        """
        LOGGER.debug(
            "Capturing pedestals for %s. Block size=%s, channels=%s",
            self.board.model,
            self.block_size,
            self._channels,
        )
        self._write_readout_settings()

        total_windows = self.board.params["windows"]
        starting_windows = range(0, total_windows, self.block_size)
        num_blocks = len(starting_windows)
        required_events = self._num_captures + self._num_warmup_events
        blocks = []

        for block_idx, start_window in enumerate(starting_windows):
            LOGGER.info(f"Capturing data for block {block_idx}/{len(starting_windows)}")
            self._update_progress(
                10 + block_idx * 75 / num_blocks,
                f"Capturing block {block_idx+1}/{num_blocks}",
            )
            block = self._capture_block_or_raise(start_window, required_events)
            blocks.append(block[self._num_warmup_events :])
        return blocks

    def _capture_block_or_raise(self, start_window: int, captures: int) -> list[dict]:
        """Attempts to capture a data for the given block.

        Args:
            start_window (int): block start window
            captures (int): number of events in the block (captures + warmup)
            block_size (int): number of windows in the block

        Returns:
            list[dict]: list of events

        Raises:
            PedestalsDataCaptureError: if the necessary number of events could not be captured.
            OperationCanceledError: if pedestals generation was cancelled.
        """
        self._set_read_window(start_window)
        expected_block = self._calculate_expected_window_labels(
            start_window, self.block_size
        )
        self._start_readout()
        try:
            with AcquisitionManager(self.board).create_temporary() as acq:
                acq.set_output()
                return self._get_valid_events_or_raise(acq, expected_block, captures)
        except Exception as e:
            raise
        finally:
            self._stop_readout()

    def _get_valid_events_or_raise(
        self,
        acq: RemoteAcquisition,
        expected_block: list[int],
        count: int,
        attempts: int = 5,
    ) -> list[dict]:
        """Attempts to get validated events for the given block.

        Args:
            acq (RemoteAcquisition): the output acquisition to pull events from.
            expected_block (list[int]): the expected window labels
            count (int): number of events (captures + warmup)
            attempts (int): number of attempts. After each failed attempt,
                the sleep time will increase.

        Returns:
            list[dict]: list of validated events

        Raises:
            PedestalsDataCaptureError: if the necessary number of events could not be captured.
            OperationCanceledError: if pedestals generation was cancelled.
        """
        events = []
        for _ in range(attempts):
            needed_amount = count - len(events)
            stream = self._stream_valid_events(
                acq,
                start=-1,
                expected_block=expected_block,
            )
            try:
                events.extend(itertools.islice(stream, needed_amount))
                return events
            except TimeoutError:
                LOGGER.debug(
                    "Didn't get enough events (%s out of %s), increasing sleep time",
                    len(events),
                    count,
                )
                self._increase_sleeptime()
            except OperationCanceledError:
                raise
        msg = (
            "Failed to capture enough events. The board may be unresponsive "
            "and need to be power cycled/reinitialized."
        )
        raise PedestalsDataCaptureError(msg)

    def _stream_valid_events(
        self, acq: RemoteAcquisition, start: int, expected_block: list[int]
    ) -> Iterator[dict]:
        """A generator for validated events.

        Args:
            acq (RemoteAcquisition): the acquisition
            count (int): number of events to stream
            start (int): start event in the acquisition
            expected_block (list[int]): expected window labels
        """
        stream = acq.stream_parsed(
            timeout=self._sleep_time,
            start=start,
            skip_bad=True,
        )
        for event in stream:
            self._raise_if_canceled()
            if self._validate_event(event, expected_block):
                # debug events need to be a full copy, since
                # subclasses can do weird things with the events
                self._debug_raw_events.append(copy.deepcopy(event))
                yield event

    def _write_readout_settings(self):
        """Prepare the board for readout by writing necessary readout settings."""
        block_size = self.block_size
        windows = self.board.params["windows"]
        rc = get_readout_controller(self.board)
        try:
            rc.set_readout_channels(self._channels)
            rc.set_read_window(windows=block_size, write_after_trig=windows)
        except Exception as e:
            LOGGER.debug("Setting the windows failed due to %s", e)

    def _validate_event(self, event: dict, expected_block: list[int]) -> bool:
        """Returns true if the window labels matches the expected_block.

        The validation matches the received window_labels with the expected
        window labels to make sure the block contains only data from that
        block. The firmware buffer sometimes contains more data from a previous block
        this makes sure it doesn't enter the next block buffer.

        Args:
            event (dict): event to validate
            expected_block (list): a list of expected window numbers

        Returns:
            True if validated, False if the events windows doesn't match expected.
        """
        test_channel = self._channels[0]
        try:
            if np.all(event["window_labels"][test_channel] == expected_block):
                return True
        except Exception as error_msg:
            LOGGER.error(f"Event validation failed due to: {error_msg}")
            return False
        LOGGER.warning(
            "Expected: %s != returned: %s",
            expected_block,
            event["window_labels"][test_channel],
        )
        return False

    def _calculate_expected_window_labels(self, start_window, block_size) -> list[int]:
        """Calculate the expected window labels for a block.

        Args:
            start_window (int): start window of the block.
            block_size (int): Number of windows captured per block.

        Returns:
            List of expected window numbers.
        """
        windows = self.board.params["windows"]
        return np.arange(start_window, start_window + block_size) % windows

    # ================================================================================
    # Readout
    # ================================================================================
    def _start_readout(self):
        """Start a readout"""
        readout_settings = {
            "trig": "imm",
            "lb": "forced",
        }
        get_board_controller(self.board).start_readout(**readout_settings)

    def _stop_readout(self):
        """Stop the readout"""
        get_board_controller(self.board).stop_readout()

    def _set_read_window(self, start_window: int):
        """Set the read window from the given start window.

        Args:
            start_window (int): the start window of the block (lookback)
        """
        get_readout_controller(self.board).set_read_window(
            windows=self.block_size,
            lookback=start_window,
            write_after_trig=self.board.params["windows"],
        )

    # ================================================================================
    # Processing
    # ================================================================================
    def _create_empty_pedestals(self, num_captures: int):
        """Build the structure for raw pedestals data."""
        return {
            "data": np.full(
                shape=(
                    self.board.params["channels"],
                    self.board.params["windows"],
                    self.board.params["samples"],
                ),
                fill_value=np.nan,
            ),
            "rawdata": np.full(
                shape=(
                    self.board.params["channels"],
                    self.board.params["windows"],
                    self.board.params["samples"],
                    num_captures,
                ),
                fill_value=np.nan,
            ),
        }

    def _store_raw_data(self, blocks: list[list[dict]]):
        """Store raw data from blocks into the pedestals dict.

        Args:
            blocks (list[list[dict]]): blocks to store
        """
        block_size = self.block_size
        raw_data = self.board.pedestals["rawdata"]
        for block_idx, block in enumerate(blocks):
            for capture_number, event in enumerate(block):
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
                            raw_data[chan, window, sample][capture_number] = data

    def _store_averaged_data(self):
        """Generate processed pedestals data from the raw data."""
        raw_data = self.board.pedestals["rawdata"]
        self.board.pedestals["data"] = np.nanmean(raw_data, axis=3)

    # ================================================================================
    # Metadata
    # ================================================================================
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

    def _store_board_metadata(self):
        """Store board params/registers into pedestals metadata"""
        self.metadata.set_configuration(self.board)

    def _store_sensor_readings(self):
        """Store sensor readings into pedestals metadata"""
        LOGGER.debug("Storing sensor metadata")
        self.metadata.store_sensor_readings(self.board)

    # ================================================================================
    # Import/Export
    # ================================================================================
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
            with gzip.GzipFile(filename, "wb", compresslevel=4) as f:
                pickle.dump(pedestals, f, protocol=pickle.HIGHEST_PROTOCOL)
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
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"No file found: {filename}")
        try:
            with gzip.GzipFile(filename, "rb") as f:
                outped = pickle.load(f)
        except EOFError as error_msg:
            LOGGER.error("Reached the end of the file, msg: %s", error_msg)
        except IOError as error_msg:
            LOGGER.error("File could not be loaded. %s", error_msg)
        except pickle.UnpicklingError as error_msg:
            LOGGER.error("Loading pedestals failed: %s", error_msg)
        else:
            if not isinstance(outped, dict):
                raise TypeError(f"Not a valid Pedestals file: {filename}")
            self.board.pedestals = outped
            return outped

    # ================================================================================
    # Helpers
    # ================================================================================
    def _recompute_sleep_time(self):
        """Recompute `self._sleeptime` using generation parameters."""
        self._sleep_time = event_transfer_time(
            self.board,
            windows=self.block_size,
            channels=len(self._channels),
            margin=self._margin,
            overhead=0.5,
        )
        LOGGER.debug("Waittime changed to %s", self._sleep_time)

    def _increase_sleeptime(self, current_amount=0, needed_amount=1):
        """Increase the sleeptime based on received vs expected.

        Formula is intended to change the margin incrementally without
        causing to much oscillation.
        """
        # Settles at 0.38
        factor = ((needed_amount - current_amount) / needed_amount) / 3 + 1
        self._margin = min(self._margin * factor, 5)
        self._recompute_sleep_time()

    def _raise_if_canceled(self):
        """Raise an ``OperationCanceledError`` if the cancel flag is set."""
        if self._cancel:
            raise OperationCanceledError("Pedestals generation was canceled.")

    def _update_progress(self, percent: float, message: str):
        """Updates a progress "receiver" with a percent and message.

        The receiver can be a list or deque of (percent, message) tuples,
        or a ProgressDialog (for use with NaluScope).

        Args:
            percent (float): the percent completion of the task
            message (str): a description of what is currently taking place
        """
        progress = self._progress
        if progress is None:
            LOGGER.debug("%s | %s", percent, message)
            return
        else:
            progress.append((percent, message))
