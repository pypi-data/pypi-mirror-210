"""AARDVARCv3
"""
import time
from collections import deque
from logging import getLogger

from naludaq.controllers import get_board_controller, get_readout_controller
from naludaq.tools.pedestals.pedestals_controller import PedestalsController, sleep_calc

LOGGER = getLogger("naludaq.aardvarcv3_pedestals_generator")


class AAv3PedestalsController(PedestalsController):
    def __init__(
        self,
        board,
        num_captures: int = 10,
        num_warmup_events: int = 10,
        channels: "list[int]" = None,
    ):
        super().__init__(board, num_captures, num_warmup_events, channels=channels)
        self.margin: float = 2.0
        self.sleeptime: float = sleep_calc(board, self.margin, len(self._channels))

    def _capture_block(self, block, block_size, num_captures, num_warmup_events):
        num_captures = num_captures or self.num_captures
        num_warmup_events = num_warmup_events or self.num_warmup_events
        total_captures = num_captures + num_warmup_events

        self.validated_data = deque(maxlen=num_captures)
        get_readout_controller(self.board).set_read_window(lookback=block * block_size)

        t_count = 0
        timeout = 5

        while len(self.validated_data) < total_captures:
            # If not data is received after timeout, there is no recovery.
            if t_count > timeout:
                return False
            # Make sure buffer is empty
            self.block_buffer = deque(maxlen=total_captures + 1)
            self._daq.output_buffer = self.block_buffer

            needed_amount = total_captures - len(self.validated_data)
            if needed_amount <= 0:
                break

            # The capture logic, sw trigger and wait.
            self._start_capture()
            for _ in range(needed_amount + 1):
                get_board_controller(self.board).toggle_trigger()
                time.sleep(self.sleeptime)
            self._stop_capture()

            #  First window contains a bug, TODO: Fix me when bug in chip is fixed.
            try:
                _ = self.block_buffer.popleft()
            except IndexError:
                pass

            if len(self.block_buffer) != needed_amount:
                LOGGER.debug("data capture failed, restarting")
                self._increase_sleeptime(needed_amount)

            expected_block = self._calculate_expected_block(block, block_size)
            if not self.block_buffer:  # Rest of the logic require data.
                LOGGER.debug(
                    "Pedestals buffer is empty, indicating transmission error, retrying."
                )
                t_count += 1
                continue
            LOGGER.debug(
                "Only keep validated events, need: %s, from %s",
                needed_amount,
                len(self.block_buffer),
            )
            if self._only_keep_validated_events(
                self.block_buffer,
                self.validated_data,
                self._warmup_data if self._store_warmup_events else None,
                expected_block,
                num_captures,
                num_warmup_events,
            ):
                return True

        return True

    def _start_capture(self):
        """Start board and daq capture"""
        readout_settings = {
            "trig": "ext",
            "lb": "forced",
            "acq": "pedsub",
            "dig_head": False,
            "ped": "zero",
            "readoutEn": True,
            "singleEv": False,
        }
        self._daq.start_capture()
        get_board_controller(self.board).start_readout(**readout_settings)

    def _stop_capture(self):
        """Stop board and daq"""
        self._daq.stop_capture()
        get_board_controller(self.board).stop_readout()
        self._daq.stop_workers()
