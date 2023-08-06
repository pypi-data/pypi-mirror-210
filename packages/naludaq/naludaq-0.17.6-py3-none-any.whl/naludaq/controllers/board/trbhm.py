"""
"""
from logging import getLogger

from naludaq.communication import ControlRegisters

from .default import BoardController

LOGGER = getLogger("naludaq.board_controller_trbhm")


class TrbhmBoardController(BoardController):
    """Special board controller for TRBHM."""

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

    def toggle_trigger(self):
        """Toggles the ext trigger using software.

        For TRBHM the wait between separate register writes is too long, and
        toggling the trigger too slowly results in too many events coming back
        and filling the FIFO, causing malformed events. This method instead
        sends the register writes all as one string.
        """
        cr = ControlRegisters(self.board)

        wait_cmd = "AE000001"
        exttrig_high_cmd = cr.generate_write("exttrig", True)
        exttrig_low_cmd = cr.generate_write("exttrig", False)
        toggle_cmd = wait_cmd + exttrig_high_cmd + exttrig_low_cmd
        self._send_command(toggle_cmd)

    def set_loopback_enabled(self, enabled: bool):
        """Set whether serial loopback is enabled.

        Loopback can safely be disabled during most of the operations with the board.
        Loopback **must** be disabled when communicating over the serial interface.
        If serial communication with the ASIC is intended then this should run during startup and only be enabled as needed.

        Args:
            enabled (bool): True to enable loopback.

        Raises:
            TypeError if enabled is not a bool.
        """
        if not isinstance(enabled, bool):
            raise TypeError("Argument must be bool")
        OFF = "B0900002"
        ON = "B0900003"
        cmd = ON if enabled else OFF
        self._send_command(cmd)
