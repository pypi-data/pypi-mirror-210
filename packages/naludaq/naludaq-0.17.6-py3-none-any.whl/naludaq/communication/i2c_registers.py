import logging

from naludaq.backend.managers.io import BoardIoManager
from naludaq.communication import registers
from naludaq.helpers.exceptions import I2CError, InvalidBoardModelError
from naludaq.helpers.semiton import SemitonABC

logger = logging.getLogger("naludaq.i2c_registers")


class I2CRegisters(registers.ReadRegisters, registers.WriteRegisters, SemitonABC):
    def __init__(self, board):
        """Communication with I2C devices through FPGA registers.

        Args:
            board (Board): the board object.
        """
        if "i2c_registers" not in board.registers:
            raise InvalidBoardModelError(
                f'Board "{board.model}" is missing I2C registers or does not support I2C'
            )

        super().__init__(board, "i2c_registers")
        self._write_cmd = 0xAF
        self._read_cmd = 0xAD
        self.width_cmd = 2
        self.width_addr = 2  # hex char
        self.width_val = 4  # hex char

        # These are the same on all valid boards
        self._i2c_transmit_command = board.params.get("i2c", {}).get(
            "transmit_command", "CA000000"
        )

    def transmit_command(self):
        """Send the command which tells the board to transmit data over the I2C bus"""
        try:
            # Tell board to fire i2c commands
            if self.board.using_new_backend:
                BoardIoManager(self.board).write(self._i2c_transmit_command)
            else:
                self.board.connection.send(self._i2c_transmit_command)
        except Exception as e:
            raise I2CError("Failed to initiate I2C send") from e
