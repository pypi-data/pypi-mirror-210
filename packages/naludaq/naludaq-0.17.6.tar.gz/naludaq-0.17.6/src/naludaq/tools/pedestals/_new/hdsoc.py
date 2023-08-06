import logging
from typing import Iterator

from naludaq.backend.models.acquisition import RemoteAcquisition
from naludaq.controllers import get_readout_controller

from .aav3 import PedestalsGeneratorAardvarcv3New

LOGGER = logging.getLogger(
    "naludaq.pedestals_controller_hdsoc_new"
)  # pylint: disable=invalid-name


class PedestalsGeneratorHdsocNew(PedestalsGeneratorAardvarcv3New):
    """Pedestals generator for HDSoC + naludaq_rs.

    It's the same as the AARDVARCv3 pedestals generator, but with a a special fix
    which accounts for the first window being invalid. When the first window fix
    is enabled, the first window of every event captured is thrown away, since
    the first window is usually (always?) invalid. This will not affect the structure
    of the generated pedestals; all windows are still present in the output.
    """

    def __init__(
        self, board, num_captures: int, num_warmup_events: int, channels: list[int]
    ):
        super().__init__(board, num_captures, num_warmup_events, channels)
        self._first_win_fix = self.board.params.get("first_window_fix", True)

    @property
    def first_window_fix(self) -> bool:
        """Get/set whether the first window fix is enabled.
        The default is True unless otherwise specified in the board parameters.

        See the class documentation for more information on the first window fix.
        """
        return self._first_win_fix

    @first_window_fix.setter
    def first_window_fix(self, enabled: bool):
        if not isinstance(enabled, bool):
            raise TypeError("Type must be boolean")
        self._first_win_fix = enabled

    def _set_read_window(self, start_window: int):
        """Set the read window from the given start window.

        Reimplemented to account for the first window fix.
        If the first window fix is enabled, the actual start window is one less
        so that we can throw it away later, and the block size is one window more
        so we can still read until the end of the block.

        Args:
            start_window (int): the start window of the block (lookback)
        """
        get_readout_controller(self.board).set_read_window(
            windows=self._correct_block_size(self.block_size),
            lookback=self._correct_start_window(start_window),
            write_after_trig=self.board.params["windows"],
        )

    def _stream_valid_events(
        self, acq: RemoteAcquisition, start: int, expected_block: list[int]
    ) -> Iterator[dict]:
        """Generator for validated events. Does not yield any bad events,
        they are just skipped.

        Reimplemented to account for the first window fix.
        If the first window fix is enabled, the first window is thrown away
        from all events.

        Args:
            acq (RemoteAcquisition): the acquisition to stream from
            start (int): the start event in the acquisition
            expected_block (list[int]): the expected window labels
        """
        for event in super()._stream_valid_events(acq, start, expected_block):
            if self._first_win_fix:
                # this function operates in-place
                self._remove_first_window(event)
            yield event

    def _calculate_expected_window_labels(
        self, start_window: int, block_size: int
    ) -> list[int]:
        """Calculate the window labels we expect to see from an event
        read from the given block.

        Reimplmented to account for the first window fix.
        If the first window fix is enabled, the actual start window is one less
        so that we can throw it away later, and the block size is one window more
        so we can still read until the end of the block.

        Args:
            start_window (int): the start window of the block
            block_size (int): the block size

        Returns:
            list[int]: the expected window labels
        """
        return super()._calculate_expected_window_labels(
            self._correct_start_window(start_window),
            self._correct_block_size(block_size),
        )

    def _remove_first_window(self, event: dict):
        """Remove the first window from the event in-place.

        Args:
            event (dict): the event
        """
        samples = self.board.params.get("samples", 32)
        for li, lbl in [
            (i, lbl) for i, lbl in enumerate(event["window_labels"]) if len(lbl) > 0
        ]:
            event["window_labels"][li] = lbl[1:]
        for li, dat in [
            (i, dat) for i, dat in enumerate(event["data"]) if len(dat) > 0
        ]:
            event["data"][li] = dat[samples:]
            event["time"][li] = dat[samples:]

    def _correct_start_window(self, start_window: int) -> int:
        """Correct the given start window by subtracting one
        when the first window fix is enabled. Does nothing
        if the switch is off.
        """
        if self.first_window_fix:
            start_window -= 1
            if start_window < 0:
                start_window = self.board.params["windows"] - 1
        return start_window

    def _correct_block_size(self, block_size: int) -> int:
        """Correct the block size by adding one when the first
        window fix is enabled. Does nothing when the switch is off.
        """
        if self.first_window_fix:
            block_size = min(block_size + 1, self.board.params["windows"])
        return block_size
