"""Analog registers
===================
Registers controlling the analog part of the ASIC.

What are the analog registers?
It's a set of registers on the FPGA matching a set of registers on the chip
By changing these registers it controls the analog portion of the chip.

Command structure:
------------------
Updating the analog command uses a format 'BXMAAVVV'

- B tells the FPGA command parser to expect a analog/digital command.
- M is mode, 0 = write, 1 = read
- AA = address
- VVV = value

Will be interpereted by the FPGA as hex. it's 32-bit = 8 hex values.

Functions:
----------
- write_all
- write
- write2addr


"""
from logging import getLogger

from naludaq.communication import registers

LOGGER = getLogger(__name__)


class AnalogRegisters(registers.WriteRegisters):
    def __init__(self, board):
        super().__init__(board, "analog_registers")

        self._write_cmd = (
            0xB00  # Standard analog write address, changes with board/mode.
        )
        self.width_cmd = 3
        self.width_addr = 2  # hex char
        self.width_val = 3  # hex char

    # READ #########################################################

    def _get_value_from_addr(self, addr):
        """Generate the value from the hex address.

        An address can contain multiple registers.
        Generate the value depending on the bit positions of all registers on the address.

        Args:
            addr(str): Hex value of the address, 2 hex char long.

        Returns:
            integer value of the combined registers.

        Raises:
            AttributeError if the address is not valid.
        """
        addr = addr.upper()
        value = 0
        failed = True
        strobe_correction_keys = self.board.params.get("strobe_correction_keys", [])
        strobe_values_correction = self.board.params.get(
            "strobe_values_correction", False
        )
        for key, val in self.registers.items():

            if val["address"].upper() != addr:
                continue
            failed = False
            key_value = val["value"]
            key_pos = val["bitposition"]
            key_width = val["bitwidth"]

            # FIX TIMING REGS, ACCORDING TO BOARD PARAMETER timing_correction
            if strobe_values_correction and key in strobe_correction_keys:
                key_value = self._fix_timing(key_value)

            value += 2**key_pos * (int(key_value) % (2**key_width))
        if failed is True:
            raise AttributeError("Address is not found")

        return value

    def _generate_write_request(self, addr: str, value: int) -> str:
        """Generate the string to send to the board.

        OVERLOAD the standard way of generating the command since the analog command parsing
        sometimes

        Abstracts the model differences away from the main code, AARDVARCv2 got a timing hack.

        Args:
            board(obj)
            name(str): name of the analog register
            value(): Value to set the register to.
        """

        write_addr = f"{self._write_cmd:X}"
        cmd_addr = addr

        if len(addr) == 3:
            write_addr = f"B{addr[0]}0"
            cmd_addr = f"{addr[1:]}"

        if isinstance(value, (int, bool)):
            value = f"{value:X}".zfill(self.width_val)

        command = f"{write_addr}{cmd_addr}{value}"  # First 5 hex chars, address should be 3 hex. B001c

        return command

    @staticmethod
    def _fix_timing(in_value: int):
        """The timing signal data mux is all mixed up for simplicity of routing, so this fixes it

        Don't use unless you know what it does. Contains hardcoded values.
        """
        if in_value < 64:
            return in_value * 2 + 1
        return 254 - 2 * in_value
