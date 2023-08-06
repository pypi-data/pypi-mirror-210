"""Digital Registers
====================
Registers controlling the digital part of the ASIC.

This is reliant on the digital_registers portion of the .yml file.

These registers control the digital side of the ASICs.
By changing these registers it's possible to
change how and what the ASIC is reading.

Command structure:
------------------
Updating a digital command uses a format 'B01AAVVV'

- B tells the FPGA command parser to expect a analog/digital command.
- M is mode, 0 = write, 1 = read
- AA = address
- VVV = value

Will be interpereted by the FPGA as hex. it's 32-bit = 8 hex values.

Example:
---------

.. code-block: python

    dc = DigitalRegisters(board)
    dc.read("regname")
    dc.write("regname", intvalue)

"""
from logging import getLogger

from naludaq.communication import registers

LOGGER = getLogger(__name__)


class DigitalRegisters(registers.ReadRegisters, registers.WriteRegisters):
    """Digital Registers

    Attributes:
        board:
    """

    def __init__(self, board):
        super().__init__(board, "digital_registers")
        # self.parse_answer = get_answer_parser()
        self._write_cmd = 0xB01
        self._read_cmd = 0xB42
        self.width_cmd = 3
        self.width_addr = 2  # hex char
        self.width_val = 3  # hex char

    def write_all(self):
        """Write all software registers to the hardware.

        Writes all registers on the board-object to the physical board.
        It will send all the commands one by one to the board.
        Effectively syncing the software registers with the board by
        sending all values in the software to the board.
        """
        addresses = self._multichip_fix(self.list_addresses())
        for addr in addresses:
            self._write_register_or_raise(addr)

    def _multichip_fix(self, addresses):
        """Fix for multichip boards.

        If the board is a multichip board, the chip_id register
        should not be written to the board.
        """
        if self.board.params.get("num_chips", 1) != 1:
            try:
                chip_id_addr = self._get_addr_from_name_or_raise("chip_id")
                addresses.remove(chip_id_addr)
            except ValueError:
                pass
        return addresses

    def _read_all_new(self):
        """Read all registers [BETA].

        Returns:
            dict: register values structured as {reg_name: reg dict}
        """
        # Digital registers have no command ID, so we need to read them synchronously
        values = {}
        for reg_addr in self.list_addresses():
            response = self._read_from_hardware(reg_addr)
            reg = self._parse_response_to_names(response, reg_addr)
            values.update(reg)
        return values

    @registers.clear_buffer
    def read_many(self, names: list[str]) -> list[str]:
        """Read several registers at once.

        Args:
            names (Iterable[str]): names of registers to read

        Returns:
            list[int]: list of register values in the same order as provided.
        """
        self._validate_names_or_raise(names)

        # Digital registers don't have command IDs so concurrent reads are dangerous
        return [self.read(name)["value"] for name in names]
