"""UDC16 pedestals generatior.

No blocks, readout the entire 64 widnows in one sweep.
"""

import logging
import time
from collections import deque

import numpy as np

from naludaq.controllers import get_board_controller
from naludaq.helpers.exceptions import PedestalsDataCaptureError
from naludaq.tools.pedestals.pedestals_controller import (
    PedestalsController,
    _update_progress,
    increase_margin,
    sleep_calc,
)

LOGGER = logging.getLogger("naludaq.udc16_pedestal_generator")


class UDC16PedestalsGenerator(PedestalsController):
    def __init__(
        self,
        board,
        num_captures: int = 10,
        num_warmup_events: int = 10,
        channels: "list[int]" = None,
    ):
        super().__init__(
            board, num_captures, channels=None
        )  # Cannot select channels on UDC16

        self.sleeptime = 2.5  # sleep_calc(self.board, self.margin)
        self.num_warmup_events = 0

    def _capture_data_for_pedestals(
        self,
        num_captures: int = None,
        num_warmup_events: int = 0,
        channels: list = None,
        retries: int = 10,
    ) -> list:
        """Read the data for pedestals generation.

        Reads several samples from each block to average the data.
        This data is stored in the pedstore after beging processed in the
        data processing pipeline.

        Tells the board to capture events.

        Args:
            num_captures (int): number of events used to generate pedestals.
            warmup_events(int): number of warmup captures before events used for pedestals.
            channels (list): list of channels to capture for, or `None`
                to readout all channels
            retries (int): amount of retries if no valid data is captured
        """
        if num_captures is None:
            num_captures = self.num_captures
        self.num_warmup_events = num_warmup_events
        total_amount = num_captures + num_warmup_events
        needed_amount = total_amount
        prev_amount = -1
        tcnt = 0
        buffer = deque()

        LOGGER.debug("Capturing data for pedestals")
        # STATUS UPDATES ####################################
        min_value = 0
        max_value = 90
        step_value = (max_value - min_value) / total_amount
        #####################################################

        self._daq.start_capture()

        while len(buffer) < total_amount and not self._cancel:
            needed_amount = max(total_amount - len(buffer), 1) + 1
            LOGGER.debug("New run: %s", needed_amount)
            initial_data = self._get_data(
                needed_amount,
                prog_min=step_value * len(buffer),
                prog_max=max_value,
            )
            # When running in a thread, cancel to stop
            if self._cancel:
                return

            # validate captured data
            validated_data = deque()
            for evt in initial_data:
                if self._validate_event(evt):
                    validated_data.append(evt)
            LOGGER.debug(f"Validated: {len(validated_data)}/{len(initial_data)}")

            buffer.extend(validated_data)

            if len(initial_data) < needed_amount:
                self._clear_input_buffer()

            # No valid data captured
            if len(buffer) == prev_amount:
                tcnt += 1
                if tcnt >= retries:
                    break
            prev_amount = len(buffer)

        if len(buffer) < total_amount:  # This happends on timeout
            raise PedestalsDataCaptureError(
                f"Not enough data captured {len(buffer)}/{total_amount}"
            )

        pedestals_data = list(buffer)[
            -self.num_captures :
        ]  # deque doesn't support indexing

        # self.validated_data is used to generate pedestals
        self.validated_data = pedestals_data

    def _clear_input_buffer(self):
        """Make sure all data is cleared from all buffers"""
        while self.board.connection.in_waiting:
            self.board.connection.reset_input_buffer()
            time.sleep(0.1)

    def _get_data(self, amount: int, prog_min: int = 0, prog_max: int = 90):
        """Try to capture the amount of even, no amount guaranteed.

        This function fires `amount` software triggers to the board and waits
        enough time to receive them. Doesn't guarantee the data though and
        validation should be used.

        Keep track of progress using the prog_min and _max

        Args:
            amount (int): desired amount of data
            prog_min (int): minumum progress
            prog_max (int): maximum progress

        Returns:
            collections.deque with the events captured
        """
        prog_step = (prog_max - prog_min) / (amount or 1)

        self.brd_ctrl = get_board_controller(self.board)
        self._clear_input_buffer()

        self._start_capture()
        time.sleep(0.1)
        # Replace with bestest code! #############################################################
        for idx in range(amount):
            _update_progress(
                self._progress,
                int(prog_min + prog_step * (idx + 1)),
                "Capturing data...",
            )
            time.sleep(0.1)
            self.brd_ctrl.toggle_trigger()
            time.sleep(self.sleeptime)
            if self._cancel:
                break

        self._stop_capture()

        return self._daq.output_buffer

    def _start_capture(self):
        """Start capturing data"""
        # self.board.connection.reset_input_buffer()
        # self.brd_ctrl.sysrst()
        while self.board.connection.in_waiting:
            self.board.connection.reset_input_buffer()
            time.sleep(0.1)
        self._daq.output_buffer = deque()
        self._daq.start_capture()
        self.brd_ctrl.toggle_trigger()

    def _stop_capture(self):
        """Stop capturing data"""
        self._daq.stop_capture()
        self._daq.stop_workers()

    def _backup_settings(self) -> dict:
        """Store relevant registers"""
        return {}

    def _restore_backup_settings(self, backup):
        """Restore backed up registers"""
        pass

    def _set_pedestals_raw_to_zero(self, num_captures):
        brd = self.board
        output = np.zeros(
            shape=(
                brd.params.get("channels", 16),
                brd.params.get("windows", 64),
                brd.params.get("samples", 64),
                num_captures,
            )
        )

        output[:] = np.NaN
        return output

    def _validate_event(self, event):
        """Check if the event has a data field, which means it's parsed"""
        try:
            _ = event["data"]
        except KeyError:
            return False
        return True

    def _generate_pedestals_data(self, rawdata=None, num_captures=None):
        """Generates the pedestals data from captured data.

        Uses captured events in the pedestals_raw_data deque
        to generate the data.

        Args:
            nCaptures (int): Number of captures, default 10
            blocksize (int): size of blocks, default 16
        """
        _update_progress(self._progress, 95, "Generating pedestals...")

        if num_captures is None:
            num_captures = self.num_captures
        if rawdata is None:
            rawdata = self.validated_data

        block_size = 1

        LOGGER.debug(
            "Generating pedestals from %s samples with blocksize: %s",
            num_captures,
            block_size,
        )

        return self._validate_and_transfer_data_to_pedestals(
            rawdata, block_size, num_captures
        )

    def _validate_and_transfer_data_to_pedestals(
        self, validated_data, block_size, num_captures
    ):
        """Move data to board.pedestals after validating.

        Since data already is prevalidated this is just a logic check,

        Args:
            block_size(int): windows per block
            num_captures(int): amount of events averaged.
        """
        board = self.board
        channels = board.params["channels"]
        samples = board.params["samples"]

        for cap, event in enumerate(validated_data[-num_captures:]):
            for chan in range(channels):
                for window in event["window_labels"][chan]:
                    for sample in range(samples):
                        real_window = list(event["window_labels"][chan]).index(window)
                        index = int(sample + real_window * samples)
                        data = event["data"][chan][index]
                        board.pedestals["rawdata"][chan][window][sample][cap] = data

        return True

    def _reset_pedestals_data(self, num_captures=None):
        """Reset all pedestals data to an empty shape.

        The shape of the empty pedestals.data is:
        [channels][windows][samples][num_captures]

        Args:
            num_captures (int): Override number of captures for pedestals generation.
                Leave as None is unsure.
        """
        if num_captures is None:
            num_captures = self.num_captures
        pedestals = self.board.pedestals
        if pedestals is None:
            pedestals = dict()
        pedestals["rawdata"] = self._set_pedestals_raw_to_zero(num_captures)
        self.board.pedestals = pedestals

    def _generate_pedestals_from_data(self):
        """Generate pedestals data and average it.

        Takes the generated pedestals data and generates the actual pedestals.
        The pedestals are stored in the controller and can be retreived with
        get_pedestals().

        """
        pedestals = self.board.pedestals
        rawdata = pedestals["rawdata"]
        output = np.nanmean(rawdata, axis=3)
        np.nan_to_num(output, nan=0, copy=False)
        pedestals["data"] = output

    def _store_time_metadata(self):
        """Store event times into pedestals metadata"""
        LOGGER.debug("Storing time metadata")
        self.metadata.store_event_times(self.validated_data)

    def _increase_sleeptime(self, needed_amount, captured_amount):
        """Increase the sleeptime based on received vs expected.

        Formula is intended to change the margin incrementally without
        causing to much oscillation.
        """
        # inc = (needed_amount / len(self.block_buffer))/2 + 1 settles at 0.45
        # inc = (needed_amount / len(self.block_buffer))/2 fails
        # inc = (needed_amount / len(self.block_buffer)) Oscillates
        block_len = max(captured_amount, 0.1)
        inc = (needed_amount / block_len) / 3 + 1  # Settles at 0.38
        self.margin = increase_margin(self.margin, margin_inc=inc, max_margin=10)
        self.sleeptime = sleep_calc(self.board, self.margin)
        LOGGER.debug("Waittime changed to %s", self.sleeptime)
