"""Pedestals generator for UPAC96
"""
import logging
import time
from collections import deque

import numpy as np

from naludaq.controllers import get_board_controller
from naludaq.controllers.board import get_board_controller
from naludaq.helpers.exceptions import (
    OperationCanceledError,
    PedestalsDataCaptureError,
    RegisterNameError,
)
from naludaq.tools.pedestals.pedestals_controller import (
    PedestalsController,
    _update_progress,
    sleep_calc,
)
from naludaq.tools.waiter import EventWaiter

LOGGER = logging.getLogger("naludaq.upac96_pedestals_generator")


def disable_trigger_monitor_signal(func):
    """Decorator to disable the trigger monitor signal during the execution of a function.

    Args:
        func (function): function to decorate

    Returns:
        function: decorated function
    """

    def wrapper(self, *args, **kwargs):
        try:
            previous = self.board.registers["control_registers"][
                "trigger_monitor_disable"
            ]["value"]
        except KeyError:
            raise RegisterNameError("trigger_monitor_disable")
        self._board_controller.set_trigger_monitoring_disabled(disabled=True)
        result = func(self, *args, **kwargs)
        self._board_controller.set_trigger_monitoring_disabled(previous)
        return result

    return wrapper


class Upac96PedestalsGenerator(PedestalsController):
    """Pedestals generator for UPAC96.

    There are a couple differences in this pedestals generator:
    - There is no computed sleep time for data capture. Instead, an event waiter is used to stop
      as soon as an event is read.
    - The first window of all channels for each event is thrown away, leaving behind a randomly-placed
      hole in the pedestals data. The pedestals generator continues to capture events beyond the
      specified number of events (``num_captures``) until all necessary data is gathered.
    """

    def __init__(
        self,
        board,
        num_captures: int = 10,
        num_warmup_events: int = 10,
        channels: list[int] = None,
    ):
        super().__init__(
            board,
            num_captures,
            num_warmup_events=num_warmup_events,
            channels=channels,
        )
        self._board_controller = get_board_controller(board)
        self._timeout = sleep_calc(board, margin=2, channels=len(self._channels)) + 3
        self._attempts = 5

    # Capture methods =========================================================================
    @disable_trigger_monitor_signal
    def _capture_data_for_pedestals(
        self,
        num_captures: int = None,
        num_warmup_events: int = None,
    ):
        """Capture data needed for pedestals and store it in the output buffer.

        For UPAC96 it's a bit different. We need to throw away the first window and there's no forced mode,
        so it's random where the window hole shows up in the data. This capture function makes sure that
        regardless of where the hole shows up in each event, we have enough captures for all windows.

        Args:
            num_captures (int): number of data points per sample that contribute to the pedestals data.
            num_warmup_events (int): number of warmup events to capture that do not contribute to pedestals data.
        """
        channels = self._channels
        num_captures = num_captures or self.num_captures
        num_warmup_events = num_warmup_events or self.num_warmup_events
        needed_amount = num_warmup_events + num_captures
        current_amount = 0
        valid_events = []

        LOGGER.debug("Running pedestals generation...")
        self._start_capture()
        daq_buffer = self._daq.output_buffer
        while current_amount < needed_amount:
            LOGGER.info(
                "Capturing next event. Have %s, need %s", current_amount, needed_amount
            )
            _update_progress(
                self.progress,
                100 * current_amount / needed_amount,
                f"Capturing data {current_amount}/{needed_amount}",
            )
            try:
                next_event = self._next_validated_event_or_raise(
                    daq_buffer, self._timeout, self._attempts
                )
            except PedestalsDataCaptureError:
                self._stop_capture()
                raise
            except OperationCanceledError:
                LOGGER.debug("Pedestals generation canceled")
                break

            valid_events.append(next_event)

            # How long we keep reading for depends on whether we have enough data
            # for ALL windows. `current_amount` is the lowest capture amount across all windows.
            current_amount = np.min(self._get_window_counts(valid_events)[channels])

        self._stop_capture()

        self.validated_data = valid_events

    def _next_validated_event_or_raise(
        self, buffer, timeout: float, attempts: int
    ) -> dict:
        """Guaranteed to either return a valid event, or raise an error.
        This method must be called while capturing.

        Args:
            buffer (deque): daq output buffer
            timeout (float): expected timeout in seconds
            attempts (int): number of attempts

        Returns:
            dict: the event.

        Raises:
            PedestalsDataCaptureError: if a valid event could not be read.
            OperationCanceledError: if pedestals generation was canceled
        """
        event = None
        for i in range(attempts):
            self._raise_if_canceled()  # exit point for canceling
            self._toggle_trigger_or_raise()

            try:
                self._wait_for_event_or_raise(buffer, timeout)
                event = buffer.popleft()
            except (TimeoutError, IndexError):
                LOGGER.warning("Timed out while waiting for an event")
                get_board_controller(self.board).stop_readout()
                time.sleep(0.1)
                get_board_controller(self.board).digital_reset()
                time.sleep(0.25)
                get_board_controller(self.board).digital_reset()
                time.sleep(0.1)
                get_board_controller(self.board).set_continuous_mode(True)
                time.sleep(0.05)
                get_board_controller(self.board).start_readout("software")
                continue

            if self._validate_event(event):
                LOGGER.debug("Got a validated event")
                time.sleep(0.5)  # Let the trigger reset
                break
        else:
            msg = (
                "Failed to capture an event. The board may be unresponsive "
                "or need to be power cycled/reinitialized."
            )
            LOGGER.error("Failed to capture an event!")
            raise PedestalsDataCaptureError(msg)

        return event

    def _wait_for_event_or_raise(self, buffer, timeout):
        """Wait for an event or raise an error. If the function
        returns it is guaranteed that an event was read out.

        Args:
            buffer (Iterable): the daq output buffer
            timeout (float): timeout

        Raises:
            PedestalsDataCaptureError: if the event cannot be read in time.
        """
        waiter = EventWaiter(buffer, amount=len(buffer) + 1, timeout=timeout)
        try:
            waiter.start(blocking=True)
        except TimeoutError:
            raise
        except Exception as e:
            msg = "Pedestals data capture failed due to unknown reason"
            raise PedestalsDataCaptureError(msg) from e

    def _toggle_trigger_or_raise(self):
        """Toggle the external trigger or raise ``PedestalsDataCaptureError`` on failure"""
        try:
            get_board_controller(self.board).toggle_trigger()
        except Exception as e:
            msg = (
                "Pedestals data capture failed: software trigger could not "
                "be sent. Is the board connected?"
            )
            raise PedestalsDataCaptureError(msg) from e

    def _start_capture(self):
        """Start capturing data"""
        self.board.connection.reset_input_buffer()
        self._daq.output_buffer = deque()
        self._daq.start_capture()
        time.sleep(0.1)
        self._board_controller.set_continuous_mode(True)
        self._board_controller.start_readout("software")

    def _stop_capture(self):
        """Stop capturing data"""
        self._board_controller.stop_readout()
        self._daq.stop_capture()
        self._daq.stop_workers()

    # Helpers/reimplemented =========================================================================
    def _backup_settings(self) -> dict:
        """Store relevant registers"""
        return {}

    def _restore_backup_settings(self, backup):
        """Restore backed up registers"""
        pass

    def _validate_event(self, event):
        """Check if the event has a data field, which means it's parsed"""
        if "data" not in event:
            return False
        chans_with_data = [i for i, x in enumerate(event.get("data", [])) if len(x) > 0]
        return set(chans_with_data).issuperset(self._channels)

    def _get_window_counts(self, events: list[dict]) -> np.ndarray:
        """Calculate the number of times each window occurs in the given events.

        Args:
            events (list[dict]): list of validated events.

        Returns:
            np.ndarray: 2D int array with shape (channels, windows) containin
                window counts.
        """
        channels = self.board.channels
        windows = self.board.params["windows"]
        window_hits = np.zeros((channels, windows), dtype=int)

        # Count the number of times each window shows up in the data.
        for event in events:
            for chan, chan_window_labels in enumerate(event["window_labels"]):
                if len(chan_window_labels) == 0:
                    continue
                # skip first window, it's junk.
                window_hits[chan][chan_window_labels[1:-1]] += 1
        return window_hits

    # Data generation =========================================================================
    def _generate_pedestals_data(self, validated_data=None, num_captures=None):
        """Assemble the data from a list of validated events into the pedestals raw data array.
        The name of this function is extremely misleading!

        Args:
            validated_data (list[dict]): list of validated events
            num_captures (int): number of captures
        """
        num_captures = num_captures or self.num_captures
        validated_data = validated_data or self.validated_data
        num_warmup = self.num_warmup_events

        LOGGER.debug("Generating pedestals from %s samples", num_captures)
        _update_progress(self._progress, 95, "Generating pedestals...")
        channels = self.board.params.get("channels", 96)
        windows = self.board.params.get("windows", 64)
        samples = self.board.params.get("samples", 64)
        rawdata = self.board.pedestals["rawdata"]
        window_counts = np.zeros((channels, windows), dtype=int)

        for event in validated_data:
            for chan in range(channels):
                chan_data = event["data"][chan]
                for window_idx, window in enumerate(event["window_labels"][chan]):
                    if (
                        window_idx == 0 or window_idx == windows - 1
                    ):  # first window is junk
                        continue

                    cap = window_counts[chan, window] - num_warmup
                    window_counts[chan, window] += 1
                    if cap < 0 or cap >= num_captures:  # skip first few captures
                        continue

                    data = chan_data[window_idx * samples : (window_idx + 1) * samples]
                    rawdata[chan, window, :, cap] = data

        return True

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
