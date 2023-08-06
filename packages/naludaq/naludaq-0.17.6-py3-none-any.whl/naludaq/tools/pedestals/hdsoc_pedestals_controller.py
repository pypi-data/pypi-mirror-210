"""HDSoC is a special child in terms of how data is collected.
In order to generate pedestals, a sufficient amount of data needs
to be collected for every single absolute window in each channel.
However, the way data is returned with HDSoC
"""
import logging
import time
from collections import deque
from logging import getLogger

import numpy as np

from naludaq.controllers import get_board_controller, get_readout_controller
from naludaq.helpers.exceptions import OperationCanceledError, PedestalsDataCaptureError
from naludaq.tools.pedestals.pedestals_controller import PedestalsController
from naludaq.tools.waiter import EventWaiter

LOGGER = logging.getLogger(__name__)  # pylint: disable=invalid-name


from naludaq.controllers import get_board_controller, get_readout_controller
from naludaq.helpers.exceptions import NotAValidEvent, PedestalsDataCaptureError
from naludaq.helpers.helper_functions import event_transfer_time
from naludaq.tools.pedestals.pedestals_controller import PedestalsController

LOGGER = getLogger("naludaq.hdsoc_pedestals_generator")


class HDSoCPedestalsGenerator(PedestalsController):
    """HDSoC pedestals generator with firstwindow fix.

    This class is a fix for the HDSoC FW bug that causes the first window
    to be corrupted. This class will capture one extra window and discard.

    The HDSoC has a bug where you can only capture a certain amount of events before
    it needs a restart.

    This pedestals generator will work around that by starting/stopping readout multiple times per block.
    """

    def __init__(
        self,
        board,
        num_captures: int = 10,
        num_warmup_events: int = 10,
        channels: "list[int]" = None,
    ):
        super().__init__(board, num_captures, num_warmup_events, channels=channels)
        self.margin: float = 1.2
        wait_overhead = 1.0
        self._timeout: float = event_transfer_time(
            board,
            windows=board.params.get("pedestals_blocks", 16),
            channels=len(self._channels),
            margin=self.margin,
            overhead=wait_overhead,
        )
        self._attempts = 5
        self._first_win_fix = self.board.params.get("first_window_fix", True)

    def _capture_block(self, block, block_size, num_captures, num_warmup_events):
        """Capture data for a single block.

        This function overrides the parent class to capture data for a single block.

        This function works around the HDSoC FW bug to capture data
        it will capture as much data it can per run, then restart the
        readout and capture again.
        """
        num_captures = num_captures or self.num_captures
        num_warmup_events = num_warmup_events or self.num_warmup_events
        total_captures = num_captures + num_warmup_events
        block_size = block_size
        if self._first_win_fix:
            capture_size = block_size + 1  # +1 to capture the first window fix
        else:
            capture_size = block_size

        self.validated_data = deque(maxlen=num_captures)
        lb = self._get_lookback(block, block_size)
        rc = get_readout_controller(self.board)
        rc.set_read_window(
            windows=capture_size,
            lookback=lb,
        )

        self.block_buffer = []
        self._daq.output_buffer = deque(maxlen=total_captures)
        needed_amount = total_captures
        self._daq.start_capture()
        self._start_capture()
        expected_block = self._calculate_expected_block(block, block_size)
        while len(self.block_buffer) < needed_amount:
            try:
                next_event = self._next_validated_event_or_raise(
                    self._daq.output_buffer,
                    self._timeout,
                    self._attempts,
                    expected_block,
                )
            except PedestalsDataCaptureError:
                self._daq.stop_capture()
                self._daq.stop_workers()
                time.sleep(0.5)
                self._stop_capture()
                raise
            except OperationCanceledError:
                LOGGER.debug("Pedestals generation canceled")
                break

            self.block_buffer.append(next_event)

        if self._first_win_fix:
            self._remove_first_window(self.block_buffer)

        self._daq.stop_capture()
        self._daq.stop_workers()
        time.sleep(0.5)
        self._stop_capture()

        if self._store_warmup_events:
            self._warmup_data = self.block_buffer[:num_warmup_events]

        self.validated_data.extend(self.block_buffer[num_warmup_events:needed_amount])

        return True

    def _next_validated_event_or_raise(
        self, buffer, timeout: float, attempts: int, expected_block: list[int]
    ) -> dict:
        """Guaranteed to either return a valid event, or raise an error.
        This method must be called while capturing.

        Args:
            buffer (deque): daq output buffer
            timeout (float): expected timeout in seconds
            attempts (int): number of attempts
            expected_block (list[int]): list of expected windows in this block.

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
                continue

            if self._validate_event(event, expected_block):
                LOGGER.debug("Got a validated event")
                break
        else:
            msg = (
                "Failed to capture an event. The board may be unresponsive "
                "or need to be power cycled/reinitialized."
            )
            LOGGER.error("Failed to capture an event!")
            raise PedestalsDataCaptureError(msg)

        return event

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

    def _get_lookback(self, block, block_size):
        """Get lookback for the block."""
        if self._first_win_fix:
            output = block * (block_size) - 1
            if output < 0:
                output = self.board.params["windows"] - 1
        else:
            output = block * (block_size)
        return output

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
        try:
            for channel, window_label in enumerate(event["window_labels"]):
                if channel not in self._channels:
                    continue
                if not np.all(window_label[1:] == expected_block):  # Skip first window
                    LOGGER.debug(
                        "Expected: %s != returned: %s",
                        expected_block,
                        window_label[1:],
                    )
                    return False
        except Exception as error_msg:
            raise NotAValidEvent(f"Event validataion failed due to: {error_msg}")
        return True

    def _select_all_channels(self):
        """Pedestals must be generated over all channels."""
        channels_to_read = [x for x in range(self.board.params["channels"])]
        return channels_to_read

    def _start_capture(self):
        """Start board and daq capture"""
        readout_settings = {
            "trig": "ext",
            "lb": "forced",
            # "acq": "pedsub",
            # "dig_head": False,
            # "ped": "zero",
            # "readoutEn": True,
            # "singleEv": False,
        }
        get_board_controller(self.board).start_readout(**readout_settings)

    def _stop_capture(self):
        """Stop board and daq"""
        get_board_controller(self.board).stop_readout()

    def _remove_first_window(self, buffer):
        """Remove first window from buffer"""
        samples = self.board.params.get("samples", 32)
        for event in buffer:
            for li, lbl in [
                (i, lbl) for i, lbl in enumerate(event["window_labels"]) if len(lbl) > 0
            ]:
                event["window_labels"][li] = lbl[1:]
            for li, dat in [
                (i, dat) for i, dat in enumerate(event["data"]) if len(dat) > 0
            ]:
                event["data"][li] = dat[samples:]
