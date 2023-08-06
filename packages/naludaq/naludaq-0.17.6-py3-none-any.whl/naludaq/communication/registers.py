"""Base class for registers.
"""
from abc import ABC
from collections import defaultdict
from functools import wraps
from logging import getLogger
from typing import Iterable

from naludaq.backend.exceptions import ConnectionError
from naludaq.backend.managers.connection import ConnectionManager
from naludaq.backend.managers.io import BoardIoManager
from naludaq.helpers.exceptions import InvalidRegisterError

LOGGER = getLogger(__name__)


def clear_buffer(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        """Clears the board buffer before"""
        if self.board.using_new_backend:
            device = ConnectionManager(self.board).device
            if device is None:
                raise ConnectionError("There is no active connection")
            device.clear_buffers()
        else:
            self.board.connection.reset_input_buffer()
        rv = func(self, *args, **kwargs)

        return rv

    return wrapper


class Registers(ABC):
    """Base class for registers.

    By inehriting this class it will be compatible with the other register classes.
    This standardizes the way register updates are called.

    Atrributes:
    -----------

        board: The board to update the registers on.
        width_cmd (int): width of the command type in hex chars
        width_addr (int): width of the address in hex chars
        width_val (int): width of the value in hex chars
        width_total (int): total width of the command in hex chars

    """

    def __init__(self, board, register_type: str):
        self.board = board
        self._register_type = register_type
        if not isinstance(getattr(board, "registers", None), dict):
            raise InvalidRegisterError("The board is lacking valid registers")
        if not board.registers.get(register_type, None):
            raise InvalidRegisterError(f"The registers is lacking {register_type}")
        self.width_cmd = 3
        self.width_addr = 2  # hex char
        self.width_val = 3  # hex char
        self.width_total = 8  # common firmware

        self._stopword = None
        self.stopword = self.board.params.get(
            "register_stop_word",
            self.board.params["stop_word"],
        )

    @property
    def stopword(self):
        """Get/Set stopword"""
        return self._stopword

    @stopword.setter
    def stopword(self, value):
        if not isinstance(value, (int, str, bytes)):
            raise TypeError(f"stopword must be str, bytes or hex, got {type(value)}")
        elif isinstance(value, str):
            if len(value) % 2 != 0:
                raise ValueError(
                    "Since stopword converts to bytes, it must be of even length."
                )
            value = bytes.fromhex(value)
        elif isinstance(value, int):
            value = bytes.fromhex(f"{value:X}")
        self._stopword = value

    @property
    def registers(self) -> dict:
        """Shortcut to board registers"""
        return self.board.registers[self._register_type]

    @property
    def width_val_bits(self):
        """Maximum bits a value can be based on command size"""
        return self.width_val * 4

    # VALIDATIONS ############################################################
    #
    ##########################################################################
    def _validate_addr_or_raise(self, addr: str):
        """Validate the address type and make sure it exists.

        Args:
            addr(str): Hex value of address.

        Raises:
            ValueError if addr is not a valid hex or if it doesn't exist in register
            TypeError if addr is not a string or int
        """
        if not isinstance(addr, str):
            raise TypeError("Register number needs to be an integer")

        if addr.zfill(self.width_addr).upper() not in self.list_addresses():
            raise ValueError(f"Address {addr} does not exist in {self._register_type}")

    def _validate_name_or_raise(self, name):
        """Name is a user input, make sure it's valid.

        Args:
            name(str): Name of the analog register.

        Returns:
            True if name is valid, False if it's not.

        Raises:
            TypeError and ValueError
        """
        if not isinstance(name, str):
            raise TypeError(f"Name: {name} is of the wrong type: {type(name)}")
        if name.casefold() not in [k.casefold() for k in self.registers.keys()]:
            raise ValueError(f"Name: {name} is not a valid analog register.")

    def _validate_names_or_raise(self, names: Iterable[str]):
        """Validate list of register names or raise an error."""
        if not isinstance(names, Iterable):
            raise TypeError("Names must be Iterable[str]")
        for name in names:
            self._validate_name_or_raise(name)

    def _validate_value_or_raise(self, value: int, bitwidth: int):
        """Value is a user input, make sure it's valid.

        Args:
            value: Value to set the analog register to.

        Raises:
            TypeError: if the value is of the wrong type.
            ValueError: if the Value is not positive.
        """
        if not isinstance(value, (type(None), int)):
            raise TypeError(f"Value argument is of the wrong type: {type(value)}")
        if isinstance(value, int) and not 0 <= value < 2**bitwidth:
            raise ValueError("Value argument must be  a positive integer.")

    def _validate_value_map_or_raise(self, values: dict[str, int]):
        """Validate the given value map or raise an error"""
        if not isinstance(values, dict):
            raise TypeError("Values must be dict[str, int]")
        for name, value in values.items():
            self._validate_name_or_raise(name)
            bitwidth = self.registers[name]["bitwidth"]
            self._validate_value_or_raise(value, bitwidth)

    # HELPERS ################################################################
    #
    # A set of helper functions used by all registers
    #
    ##########################################################################

    def _get_addr_from_name_or_raise(self, name):
        """Returns the control registers addr from the name.

        Args:
            name(str): Name of the control register

        Returns:
            The number of the control register
        """
        if not isinstance(name, str):
            raise TypeError("Register name must be a strign")

        addr = self.registers.get(name.casefold(), False)
        if addr is False:
            raise InvalidRegisterError(f"{name} is not a valid register.")
        addr = addr["address"]
        if isinstance(addr, int):
            addr = f"{addr:X}"  # pragma: no cover
        addr = addr.zfill(self.width_addr)
        return addr.upper()

    def _validate_command_or_raise(self, command: str):
        """Make sure a generated command is of the right length."""
        if len(command) != self.width_total:
            raise ValueError(
                f"Generated command is invalid. A command must be {self.width_total} char, got {command} or length {len(command)}"
            )  # pragma: no cover

    # COMMON #################################################################
    #
    # A list of convenience tools, common for all registers.
    #
    ##########################################################################
    def list(self) -> list:
        """Lists the name of all available registers.

        Returns:
            A list of all register names
        """
        return list(k.lower() for k in self.registers.keys())

    def list_registers(self) -> dict:
        """Returns all available registers as a dict, organized in the
        same way as the registers file.

        Returns:
            A dict containing all registers
        """
        return self.registers

    def list_addresses(self):
        """Generate a list of all available addresses.

        This is useful since an address can contain multiple registers.
        The register name can correspond to one or many bits at a specific address.

        Returns:
            List of available addresses in hex (str)
        """
        reg_addr = {value["address"].upper() for value in self.registers.values()}
        return sorted(list(reg_addr), key=lambda x: int(x, 16))

    def show(self, name: str) -> str:
        """Returns the internal contents of a register.

        Args:
            name (str): The name of the register

        Returns:
            A string representation of the given register.

        Raises:
            TypeError if the name is not a string
            ValueError if the name is not a valid register
        """
        self._validate_name_or_raise(name)

        return self.registers[name]

    def _send_command(self, cmd):
        """Send request to the board"""
        if self.board.using_new_backend:
            BoardIoManager(self.board).write(cmd)
        else:
            self.board.connection.send(cmd)

    def __repr__(self):
        return f"{self.registers}(board = {self.board})"  # pragma: no cover


class WriteRegisters(Registers):
    """Writeable registers

    Adds the trait to write registers

    Functions:
    ---------

        - ``write(name, value)``
        - ``write_addr(addr, value)``
        - ``generate_write(name, value)``
        - ``generate_write_addr(name, value)``
        - ``write_all()``

    Attributes:
    -----------

        _write_cmd: the write command as a hex eg. ``0xAD``

    """

    _write_cmd = None

    # WRITE ##################################################################
    def write(self, name: str, value: int = None):
        """Set a register to a value.

        Update the internal stored reg values and
        the registers on the hardware simultaniously.

        Args:
            board
            name(str): Name of the register.
            value(int, bool): Value of the register.

        Raises:
            ValueError if name is not in register.
            TypeError if name is not a str.
        """
        self._validate_name_or_raise(name)
        name = name.lower()
        if value is not None:
            self._update_software_register(name, value)

        addr = self._get_addr_from_name_or_raise(name)

        self._write_register_or_raise(addr)

    def write_many(self, value_map: dict[str, int]):
        """Write several registers at once.

        Args:
            registers (dict[str, int]): mapping of register values to names
        """
        self._validate_value_map_or_raise(value_map)

        # update all software registers first to prevent generate_write
        # from using potentially old register values in subsequent writes
        for name, value in value_map.items():
            self._update_software_register(name, value)

        addresses = {
            self._get_addr_from_name_or_raise(name) for name in value_map.keys()
        }
        commands = [self.generate_write_addr(addr) for addr in addresses]
        command = "".join(commands)
        self._send_command(command)

    def write_addr(self, addr: "int|str", value=None):
        """Updates value on both board from register addr.

        You better know what you are doing if you use this function since it'll
        overwrite the entire address.

        This means several registers might get overwritten!

        If a value is left out the function will use whatever value is previously stored.
        The intent is to be able to write to registers that have no name yet.

        Args:
            addr (hex or int): the addr can either be hex or integer.
            value: the value sent to the board.

        Raises:
            ValueError if value is not a positive integer
            TypeError if name is not a str.
        """
        if isinstance(addr, int):
            addr = f"{addr:X}"
        self._validate_addr_or_raise(addr)
        addr = addr.zfill(self.width_addr)
        addr = addr.upper()  # All hex is uppercase

        if value is not None:
            self._update_software_register_addr(addr, value)

        self._write_register_or_raise(addr)

    def write_all(self):
        """Write all software registers to the hardware.

        Writes all registers on the board-object to the physical board.
        It will send all the commands one by one to the board.
        Effectively syncing the software registers with the board by
        sending all values in the software to the board.
        """
        if self.board.using_new_backend:
            return self._write_all_new()
        for addr in self.list_addresses():
            self._write_register_or_raise(addr)

    def _write_all_new(self, batch_size: int = 32):
        """Version of the write_all command that writes commands simulataneously.

        Args:
            batches (int): number of commands per batch to send.
                Don't make this too high, since serial/d2xx connections are
                synchronous and so large batches can result in a request timeout
                before the server finishes writing.
        """
        addresses = self.list_addresses()
        command_batches = [
            [self.generate_write_addr(addr) for addr in addresses[i : i + batch_size]]
            for i in range(0, len(addresses), batch_size)
        ]
        for commands in command_batches:
            BoardIoManager(self.board).write_all(commands)

    def _write_register_or_raise(self, addr):
        """Write a control register to the board using the register addr.

        Uses the value stored in the software and sends to the hardware.

        Args:
            addr(str): The hex address for the register as str.

        Raises:
            TypeError: if addr is not an str
            ValueError: if reg_num is not a valid register.
        """
        addr = addr.upper()
        self._validate_addr_or_raise(addr)
        value = self._get_value_from_addr(addr)

        cmd = self.generate_write_addr(addr, value)

        self._send_command(cmd)

    # GENERATE ###############################################################
    #
    # A series of commands the generates the commands to send and returns a hex str.
    #
    ##########################################################################
    def generate_write(self, name: str, value: int = None) -> str:
        """Generates a command string for writing to a register.

        This function does not change any hardware or software registers.

        Args:
            name (str): the name of the register
            value (int): the value, or None to use the value held in the software register.

        Returns:
            The command string

        Raises:
            ValueError if the address, value or generated command is invalid
            TypeError if the value is an invalid type
        """
        self._validate_name_or_raise(name)
        name = name.lower()
        addr = self._get_addr_from_name_or_raise(name)
        # Fix total comand for address

        if value is not None:
            addr_val = int(self._get_value_from_addr(addr))
            bw = self.registers[name]["bitwidth"]
            bp = self.registers[name]["bitposition"]
            self._validate_value_or_raise(value, bw)
            mask = (2**bw - 1) << bp
            value = addr_val - (addr_val & mask) + ((value & (2**bw - 1)) << bp)

        try:
            cmd = self.generate_write_addr(addr=addr, value=value)
        except (ValueError, TypeError, AttributeError):  # pragma: no cover
            raise  # pragma: no cover
        return cmd

    def generate_write_addr(self, addr: "int|str", value: int = None) -> str:
        """Generates a command string for writing to a register.

        This function does not change any hardware or software registers.

        Args:
            addr (str): the address of the register
            value (int): the value, or None to use the value held in the software register.

        Returns:
            The command string

        Raises:
            ValueError if the address, value or generated command is invalid
            TypeError if the value is an invalid type
        """
        if isinstance(addr, int):
            addr = f"{addr:X}"
        if not isinstance(addr, str):
            raise TypeError("address should be either a hex string or hex (0xADDR)")
        addr = addr.zfill(self.width_addr)
        addr = addr.upper()

        if value is None:
            try:
                value = self._get_value_from_addr(addr)
            except AttributeError:
                raise ValueError(f"No value found for address {addr}")

        self._validate_value_or_raise(value, bitwidth=self.width_val_bits)

        command = self._generate_write_request(addr, value)
        self._validate_command_or_raise(command)

        return command

    def _generate_write_request(self, addr: str, value: int) -> str:
        """Generate the write command"""

        cmd = f"{self._write_cmd:X}"
        cmd_addr = addr.zfill(self.width_addr)
        val = f"{value:X}".zfill(self.width_val)
        command = f"{cmd}{cmd_addr}{val}"
        return command.upper()

    def _update_software_register(self, name: str, value: int):
        """Set boardparam digital register, do not change the state of the FPGA

        Args:
            name: Register name.
            value: Register value.
        """
        name = name.lower()
        self._validate_name_or_raise(name)
        self._validate_value_or_raise(value, bitwidth=self.registers[name]["bitwidth"])

        self.registers[name]["value"] = value

    def _update_software_register_addr(self, addr: str, value: int):
        """Update any registers sharing the addr with their part of the value"""
        self._validate_value_or_raise(
            value, bitwidth=self.width_val_bits
        )  # hex is 4 bits
        for reg in self.list_registers().values():
            if reg["address"].lower() != addr.lower():
                continue
            val = value >> reg["bitposition"]
            val &= 2 ** reg["bitwidth"] - 1
            reg["value"] = val

    def _get_value_from_addr(self, addr):
        """Generate the value from the hex address.

        An address can contain multiple registers.
        Generate the value depending on the bit positions of all registers on the address.

        Args:
            addr(str): Hex value of the address, 2 hex char long.

        Returns:
            integer value of the combined registers.

        Raises:
            AttributeError if address is not in the registers.
        """
        regs = [
            val
            for val in self.registers.values()
            if val["address"].upper() == addr.upper()
        ]
        if len(regs) == 0:
            raise AttributeError("Address not found")

        value = 0
        for val in regs:
            # key_value, key_addr, key_pos, key_width, _ = val
            key_value = val["value"]
            val["address"]
            key_pos = val["bitposition"]
            key_width = val["bitwidth"]

            # if key_addr == addr:
            value += 2**key_pos * (int(key_value) % (2**key_width))

        return value


class ReadRegisters(Registers):
    """Readable registers

    Adds the ability to read registers


    Functions:
    ---------

        - ``read(name)``
        - ``read_addr(addr)``
        - ``generate_read(name)``
        - ``generate_read_addr(name)``
        - ``read_all()``

    Attributes:
    -----------

        _read_cmd: the read address as a hex eg. ``0xAF``

    """

    _read_cmd = None

    @clear_buffer
    def read(self, name: str) -> int:
        """Read from a register with a name.

        Args:
            name: Name of the register.

        Raises:
            ValueError if name is not in register.
            TypeError if name is not a str.
        """
        self._validate_name_or_raise(name)
        name = name.lower()
        reg_addr = self._get_addr_from_name_or_raise(name)

        return_value = self._read_from_hardware(reg_addr)
        reg = self._parse_response_to_names(return_value, reg_addr)

        return reg[name]

    @clear_buffer
    def read_many(self, names: list[str]) -> list[str]:
        """Read several registers at once.

        Do not use this function to read the same register multiple times,
        as older values will be discarded.

        Args:
            names (Iterable[str]): names of registers to read

        Returns:
            list[int]: list of register values in the same order as provided.

        Raises:
            TimeoutError: if one or more registers could not be read in time.
        """
        self._validate_names_or_raise(names)

        # cannot perform concurrent reads without naludaq_rs
        if not self.board.using_new_backend:
            return [self.read(name)["value"] for name in names]

        # sort registers & generate by address to reduce # of commands
        addresses = defaultdict(list)
        for name in names:
            addr = self._get_addr_from_name_or_raise(name)
            addresses[addr].append(name)
        read_cmds = [self.generate_read_addr(addr) for addr in addresses.keys()]

        # response order is guaranteed to be the same as the commands sent
        try:
            responses = BoardIoManager(self.board).read_all(read_cmds)
        except TimeoutError:
            raise

        # parse responses into registers by address
        values = {}
        for (addr, addr_names), response in zip(addresses.items(), responses):
            response = self._parse_answer(response)["value"]
            response = self._parse_response_to_names(response, addr)
            for name in addr_names:
                values[name] = response[name]["value"]

        sorted_values = [values[name] for name in names]
        return sorted_values

    @clear_buffer
    def read_all(self, overwrite: bool = False):
        """Read all digital registers from the board.

        Reads the values based on the register number rather than the name.

        Args:
            board

        Returns:
            dictionary with {reg_num: values,}
        """
        if self.board.using_new_backend:
            return self._read_all_new()
        values = dict()
        for reg_addr in self.list_addresses():
            response = self._read_from_hardware(reg_addr)

            reg = self._parse_response_to_names(response, reg_addr)
            values.update(reg)
        return values

    def _read_all_new(self):
        """Read all registers [BETA].

        Sends read commands all at once and parses the results.

        Returns:
            dict: register values structured as {reg_name: reg dict}
        """
        addresses = self.list_addresses()
        commands = [self.generate_read_addr(addr) for addr in addresses]
        values = {}
        answers = BoardIoManager(self.board).read_all(commands)
        for address, answer in zip(addresses, answers):
            parsed_answer = self._parse_answer(answer)["value"]
            reg = self._parse_response_to_names(parsed_answer, address)
            values.update(reg)
        return values

    @clear_buffer
    def read_addr(self, addr: int) -> int:
        """Read an address and return the value.

        Args:
            addr(hex|int): 8-bit address to read as either int or hex."""
        addr = f"{addr:02X}".upper()
        return self._read_from_hardware(addr)

    def generate_read(self, name: str) -> str:
        """Generate and return the read command as hex"""
        self._validate_name_or_raise(name)
        name = name.lower()
        addr = self._get_addr_from_name_or_raise(name)
        cmd = self._generate_read_request(addr)
        return cmd

    def generate_read_addr(self, addr: "int|str") -> str:
        """Generate and return the read addr command as HEX"""
        if isinstance(addr, int):
            addr = f"{addr:X}"
        self._validate_addr_or_raise(addr)
        addr = addr.upper()
        cmd = self._generate_read_request(addr)
        return cmd.upper()

    @clear_buffer
    def _read_from_hardware(self, addr: str, *args, **kwargs) -> int:
        """Read from a digital read register with an address

        Args:
            addr: Address to read out data from.
        """
        cmd = self._generate_read_request(addr)
        try:
            if self.board.using_new_backend:
                response = BoardIoManager(self.board).read(cmd)
            else:
                self._send_command(cmd)
                response = self._read_response()
        except TimeoutError:  # pragma: no cover
            return -1  # pragma: no cover
        answer = self._parse_answer(response)
        return answer["value"]

    def _generate_read_request(self, addr: str) -> str:
        """Generate the read command for the firmwares. cmd: RRAA000"""
        cmd = f"{self._read_cmd:X}"
        cmd_addr = addr.zfill(self.width_addr)
        val = "0".zfill(self.width_val)
        command = f"{cmd}{cmd_addr}{val}"
        return command.upper()

    def _parse_response_to_names(self, buffer, addr):
        """Takes the input buffer and parses the response into the registers.

        Each register address can contain multiple register names, this function
        parses the register address into the correct names.

        Returns:
            Dictionary with the names: [val, addr, pos, width, rw]
        """
        outp = {}

        for key, val in self.registers.items():
            if val["address"].upper() == addr.upper():
                position = val["bitposition"]
                width = val["bitwidth"]
                mask = 2**width - 1
                shifted = buffer >> position
                oval = shifted & mask
                outp[key] = {}

                for regkey, regval in val.items():
                    outp[key][regkey] = regval
                outp[key]["value"] = oval

        return outp

    def _parse_answer(self, buffer):
        """Parses a raw binary answer into python data formats.

        Args:
            buffer (bytes): Response to parse.

        Returns:
            parsed answer as a dict expected format.
        """
        header = int.from_bytes(buffer[0:2], byteorder="big", signed=False)
        response = {
            "header": header,
            "read_reg": header & 255,  # only 8 lsb]
            "value": int.from_bytes(buffer[2:4], byteorder="big", signed=False),
        }

        return response

    def _read_response(self):
        """Read a data package based on the register stopword"""
        return self.board.connection.read_until(self.stopword)  # pragma: no cover


# validation #################################################################
#
##############################################################################
def validate_registermap_or_raise(registers):
    """Validate a regmap, raises error if it's not valid."""

    # invert registers
    inv_register = invert_regmap(registers)

    # find potential conflicts
    try:
        conflicts = find_conflicting_registers(inv_register)
    except Exception as e_msg:
        raise InvalidRegisterError(f"Following register have conflicting bits: {e_msg}")
    # if potential conflicts
    if conflicts:
        raise InvalidRegisterError(
            f"Following register have conflicting bits: {conflicts}"
        )

    return True


def find_conflicting_registers(registers):
    """Takes an inverted regmap and finds all conflicts

    Args:
        registers (dict): register dictionary and find all conflicts.

    Returns:
        dictionary with conflictingaddresses and conflicting names.
    """
    conflict_regs = defaultdict(list)
    inv_regmap = invert_regmap(registers)  # {addr: [(name, reg)]}
    for addr, regs in inv_regmap.items():
        if len(regs) <= 1:
            continue

        regs = sorted(regs, key=lambda i: i[1]["bitposition"])
        for idx, (name1, item1) in enumerate(regs[:-1]):
            item1_end = item1["bitposition"] + item1["bitwidth"] - 1

            for name2, item2 in regs[idx + 1 :]:
                if item2["bitposition"] > item1_end:
                    break
                conflict_regs[addr].append(name1)
                conflict_regs[addr].append(name2)

    conflict_regs = {addr: sorted(set(names)) for addr, names in conflict_regs.items()}
    return conflict_regs


def invert_regmap(registers):
    """Invert a regmap dict to return addr: register instead of name: register

    Args:
        registers (dict): register map {name: registers}

    Returns:
        Dictionary with {address: register}
    """
    all_regs = defaultdict(list)

    for key, val in registers.items():
        addr = val["address"]
        all_regs[addr].append((key, val))

    return all_regs
