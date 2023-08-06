"""Initializer for the UPAC96 board

This initializer will run the init sequence for the UPAC96 board.
It contains all UPAC96 specific startup sequence
"""
import functools
import logging
import time

from naludaq.board import initializers
from naludaq.controllers import get_board_controller, get_dac_controller

logger = logging.getLogger(__name__)


def func_print(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f" Running: {func.__name__} ".ljust(80, "#"))
        v = func(*args, **kwargs)
        return v

    return wrapper


class InitUPAC96(initializers.Initializers):
    def __init__(self, board):
        super().__init__(board, "upac96")
        self.power_sequence = [
            "pwr_udc1_en",
            "pwr_udc2_en",
        ]
        self.rxtx = [
            "udc_rxout_enable",
            "udc_txin_enable",
        ]
        self.num_chips = self.board.params.get("num_chips", 6)

        self.conn_type = self.board.connection_info.get("type", None)
        if self.conn_type not in ["uart", "ftdi", "ft60x"]:
            raise ConnectionError(f"Unsupported connection type: {self.conn_type}")

    def run(self):
        logger.info("Starting UPAC96 with %s connection", self.conn_type)
        # Enable UART

        self._select_output_buffer()

        # UDC_FPGA_register_init
        self._fpga_init()

        # POWER ON FMC BOARD
        self._power_toggle(True)

        # reset sysrst and regclr
        self._reset_sys()

        self._reset_digital()

        # Enable Rx and Tx
        self._rxtx_toggle(False)
        time.sleep(0.1)
        self._rxtx_toggle(True)

        # Analog and digital startup:
        # Digital startup
        self._digital_startup()

        # Analog_startup
        self._analog_startup()
        self._write_chip_ids()
        # UDC ASIC reset
        # self._asic_reset()

        # Set DACS
        self._init_dacs()

        # for some reason on USB there's junk left over in the buffer
        self.board.connection.reset_input_buffer()

        return True

    @func_print
    def _fpga_init(self):
        """Write all FPGA registers to their default values."""
        self.control_registers.write_all()
        self.i2c_registers.write("i2c_en", True)

    @func_print
    def _power_toggle(self, state):
        """Toggles the power rails defined in `power_sequence` attribute"""
        for register in self.power_sequence:
            self.control_write(register, state)

    def _select_output_buffer(self, enable=False):
        """Enable the uart interface and disable the usb interface"""
        # Flush fifos, disable USB & enable UART
        if self.conn_type in ["uart", "ftdi"]:
            get_board_controller(self.board).enable_uart()
        elif self.conn_type == "ft60x":
            get_board_controller(self.board).enable_usb()
        else:
            raise ConnectionError(
                f"Connection type {self.conn_type} not supported, can't start the board"
            )

    @func_print
    def _reset_sys(self):
        """Reset the ASIC and clear the analog and digital registers"""
        self.control_write("sysrst", True)
        self.control_write("sysrst", False)
        self.control_write("regclr", True)
        self.control_write("regclr", False)

    def _reset_digital(self):
        """Reset digital side of the ASIC"""
        self.control_write("digrst", True)
        self.control_write("digrst", False)

    @func_print
    def _asic_reset(self):
        """Reset the asic, analog side, digital side, and fifo"""
        self.control_write("sysrst", True)
        self.control_write("sysrst", False)
        # self._reset_digital()

    @func_print
    def _rxtx_toggle(self, state):
        """Toggles ASIC rx and tx enable. True when talking to ASIC."""
        value = 0x3F if state else 0x00
        for register in self.rxtx:
            self.control_write(register, value)

    @func_print
    def _digital_startup(self):
        """Startup the digital side by programming all registers"""
        self.digital_registers.write_all()

    @func_print
    def _write_chip_ids(self):
        """Write the chip ids to the digital registers

        This will allow the parser to recognize which chip the return data
        belongs to.
        """
        udc_rxout_enable = (
            self.board.registers["control_registers"]
            .get("udc_rxout_enable", {})
            .get("value", 0x3F)
        )
        for chip in range(self.num_chips):
            self.control_registers.write("udc_rxout_enable", 2**chip)
            self.digital_registers.write("chip_id", chip)
        self.control_registers.write("udc_rxout_enable", udc_rxout_enable)

    @func_print
    def _analog_startup(self):
        """Start the analog side of the chip"""
        self.analog_registers.write_all()

        self._write_reg1()

        # DLL START UP SEQUENCE
        self._dll_startup()

    @func_print
    def _write_reg1(self):
        """reg1 is weird, two things live at the same address.
        Need to switch between them.
        """
        self.digital_write("writemask_r", 0x0FF)
        time.sleep(0.01)
        self.analog_write("reg1", 0x100)
        time.sleep(0.01)
        self.digital_write("writemask_r", 0x1FF)
        time.sleep(0.01)
        self.digital_write("writemask_l", 0x0FF)
        time.sleep(0.01)
        self.analog_write("reg1", 0x100)
        time.sleep(0.01)
        self.digital_write("writemask_l", 0x1FF)

    @func_print
    def _dll_startup(self):
        """Starting the delay line on the analog side."""
        self.analog_write("qbias", 0)
        self.analog_write("vadjn_sw", 1)
        time.sleep(1)
        self.analog_write("qbias", 2048)
        self.analog_write("vadjn_sw", 0)

    @func_print
    def _init_dacs(self):
        """Program the left and right side DACs"""
        dacvalues = self._get_dacvalues()

        for channel, value in dacvalues.items():
            get_dac_controller(self.board).set_single_dac(channel, value)

    def _get_dacvalues(self) -> dict:
        """Return a dict with all the "channels: dac_values"""
        return self.board.params.get("ext_dac", {}).get("channels", {})
