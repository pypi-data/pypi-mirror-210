import logging

from .default import BoardController

LOGGER = logging.getLogger("naludaq.board_controller_aodsoc")


class BoardControllerAodsoc(BoardController):
    """Board controller for AODSOC boards.

    Has a special version of the `read_scalers` function to handle reading from chips
    individually.
    """

    def read_scalar(self, channel: int) -> int:
        """Read the scalar for the given channel"""
        relative_channel = self._get_relative_channel(channel)
        selected_chips = self._get_selected_chips()
        self._select_chip_by_channel(channel)
        result = super().read_scalar(relative_channel)
        self._select_chips(selected_chips)
        return result

    def _get_relative_channel(self, channel: int) -> int:
        """Get the channel relative to the chip it belongs to."""
        num_chips = self._get_num_chips()
        channels_per_chip = self.board.channels // num_chips
        return channel % channels_per_chip

    def _select_chip_by_channel(self, channel: int):
        """Enables only the chip that the given channel belongs to."""
        num_chips = self._get_num_chips()
        channels_per_chip = self.board.channels // num_chips
        chip = channel // channels_per_chip
        self._select_chips([chip])

    def _select_chips(self, chips: list[int]):
        """Select the chips enabled for RX/TX.
        Useful for reading/writing registers for a single chip.

        Args:
            chips (list[int]): list of chips that are enabled.
        """
        en = sum([1 << x for x in chips])
        self._write_control_register("ard_tx_en", en)
        self._write_control_register("ard_rx_en", en)

    def _get_selected_chips(self) -> list[int]:
        """Get the chips which are currently enabled for TX."""
        tx_en = self.board.registers["control_registers"]["ard_tx_en"]["value"]
        chips = self._get_num_chips()
        selected_chips = [(tx_en >> x) & 1 == 1 for x in range(chips)]
        return selected_chips

    def _get_num_chips(self):
        """Get the number of chips on the board"""
        return self.board.params.get("num_chips", 2)
