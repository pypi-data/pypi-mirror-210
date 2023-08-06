import time
from collections import deque

from naludaq.board import Board
from naludaq.communication import AnalogRegisters, ControlRegisters, DigitalRegisters
from naludaq.controllers import get_board_controller, get_readout_controller

# from naludaq.tools.pedestals.pedestals_controller import sleep_calc, increase_margin


class DataCollector:
    def __init__(self, daq, board: Board):
        """Wrapper for the standard readout procedure for most Nalu Scientific ASICs

        Takes all of the configuration settings for readout and updates the settings to the chip
        when readout is commenced. The Data Collector is very specific with its settings, and will
        only take in the correctly formatted settings.

        Args:
            daq (BenDaq, LightDaq): The Data acquisition object that the DataCollector will use to
                interface with the chip
            board (Board): The Board object that has the proper parameters and connection to the
                physical board
        """

        self.board = board
        self.daq = daq
        self.default_margin = 1.1
        self.margin = self.default_margin
        self.sleeptime = sleep_calc(board, self.margin)

    @property
    def board(self):
        return self._board

    @property
    def daq(self):
        return self._daq

    @board.setter
    def board(self, board):
        self._board = board

    @daq.setter
    def daq(self, daq):
        self._daq = daq

    def get_data(
        self,
        amount: int,
        trig_type: str,
        lb_type: str,
        windows: int,
        lookback: int,
        write_after_trig: int,
        channels: list,
        timeout: int = 5,
    ) -> deque:
        """Returns an exact amount of pre-processed events!

        The return is sizelimited to `amount` by a circular buffer, it'll overwrite the oldest data
        if the board returns too much data. This is by design and can't be changed.


        ## Readout Settings Explanation:
            `trig_type` (trigger_type):
                'imm' (immediate): digitize whatever instantly as fast as possible.
                'ext' (external): use the external trigger.
                'self' (self): trigger on input RF signal. Uses trigger values
            `lb_type` (lookback type):
                'forced' (forced): always reads out same set of windows, start window set by lookback
                'trigrel' (trigger relatve): relative to the trigger.
                'roi' (region of interest): complicated...

        Args:
            `amount` (int): desired amount of events, cannot be less than 1
            `trig_type` (string): How the trigger runs for the acquisition
            `lb_type` (string): The type of lookback for the acquisition
            `windows` (int): amount of windows to read. Value must be a positive integer
            `lookback` (int): how many windows the readout header goes back
            `write_after_trig` (int): how many windows are read out after the trigger signal is recieved
            `channels` (List): list of channels to be activated when reading out data
            `timeout` (int): timeout in retries per event.

        Returns:
            A deque with the events, raw or processed depending on the daq.

        Raises:
            `ValueError` if amount is < 1.
            `TimeoutError` if no data is captured in `timeout` retries.
        """

        rdt_controller = get_readout_controller(self.board)
        readout_settings = {
            "trig": trig_type,
            "lb": lb_type,
            "acq": "pedsub",  # Hardcoded because all simple readouts use this mode
            "ped": "zero",  # Hardcoded because all simple readouts use this mode
            "readoutEn": True,  # This should always be on since we always want ethernet readout
            "singleEv": True,  # Always on, make sure `amount` counter is used by FW.
        }

        window_settings = {
            "windows": windows,
            "lookback": lookback,
            "write_after_trig": write_after_trig,
        }

        self._validate_readout_settings(readout_settings)
        self._validate_window_settings(window_settings)
        self._validate_channel_settings(channels)
        if amount < 1:
            raise ValueError(f"amount cannot be less than 1")

        output_buffer = deque(maxlen=amount)
        self.daq.output_buffer = output_buffer
        desired_amount = amount
        reset_count = 0
        self.margin = self.default_margin
        rdt_controller.set_read_window(**window_settings)
        rdt_controller.set_readout_channels(channels)
        while len(output_buffer) < amount:
            desired_amount = amount - len(output_buffer)
            if desired_amount <= 0:
                break

            self.sleeptime = sleep_calc(self.board, self.margin)

            rdt_controller.number_events_to_read(desired_amount)
            self.daq.start_capture()
            get_board_controller(self.board).start_readout(**readout_settings)

            finished = self._wait_for_data(output_buffer, desired_amount)

            if not finished:
                if reset_count >= timeout:
                    raise TimeoutError(
                        f"Something wrong with setup/hardware, "
                        f"reset {timeout} times still no data."
                    )
                reset_count += 1
                self.margin = increase_margin(self.margin)
                self.sleeptime = sleep_calc(self.board, self.margin)

            self.daq.stop_capture()
            get_board_controller(self.board).stop_readout()

        return output_buffer

    def _wait_for_data(self, output_buffer, desired_amount):
        """Wait for the desired amount of data to arrive.

        Returns in these cases:
        - if desired amout is reached
        - if no data is received
        - if too much data is received

        Args:
            output_buffer (deque): storage for data we wait for.
            desired_amount(int): The amount of events we wait for.

        Returns:
            True if the correct amount of data is captured, else False
        """
        result = True
        prev_amount = -1
        # wait for readout to finish
        while len(output_buffer) != prev_amount:
            stime = self.sleeptime * (desired_amount - len(output_buffer))
            if output_buffer:
                prev_amount = len(output_buffer)
            try:  # If output_buffer is larger than desired, stime < 0.
                time.sleep(stime)
            except ValueError:
                pass
            if len(output_buffer) > desired_amount:
                # Output buffer can currently never be bigger since it's size limited.
                # Keep edge case in case someone changes the limit.
                break

        if len(output_buffer) == 0:
            result = False

        return result

    def parameter_sweep(self, parameter, numevts, param_min, param_max, param_step=1):
        """
        Iterates through values in a specified register, taking data for every value in the sweep.

        Register type (analog, digital, or control) is automatically identified.

        Args:
            parameter (str): name of register to sweep through
            numevts (int): number of events to take at each parameter value
            param_min (int): minimum parameter value
            param_max (int): maximum parameter value
            param_step (int): sweep step value

        Returns:
            List of data taken coupled with the parameter value used during that acquisition

        Raises:
            ValueError when parameter does not match existing registers
        """

        data_manifest = []

        register_controller = self._register_type_selector(parameter)

        for param_value in range(param_min, param_max, param_step):
            register_controller.write(parameter, param_value)

            data = self.get_data(numevts)
            data_row = [param_value, data]
            data_manifest.append(data_row)

        return data_manifest

    def _register_type_selector(self, parameter):
        if parameter in AnalogRegisters(self.board).registers.keys():
            reg_com = AnalogRegisters(self.board)
        elif parameter in DigitalRegisters(self.board).registers.keys():
            reg_com = DigitalRegisters(self.board)
        elif parameter in ControlRegisters(self.board).registers.keys():
            reg_com = ControlRegisters(self.board)
        else:
            raise ValueError(f"{parameter} is not a valid register name")

        return reg_com

    @staticmethod
    def _validate_readout_settings(readout_settings: dict):

        valid_readout_settings = {
            "trig": ["i", "s", "e"],
            "lb": ["t", "f", "r"],
            "acq": ["p", "r"],
            "ped": ["z", "c", "r"],
            "readoutEn": [True, False],
            "singleEv": [True, False],
        }

        # Validate values
        for key in readout_settings.keys():
            if key not in ["readoutEn", "singleEv"]:
                if readout_settings[key][0] not in valid_readout_settings[key]:
                    raise KeyError(
                        f"{readout_settings[key]} is not a valid value for {key}. Valid \
                        values are f{valid_readout_settings[key]}"
                    )
            else:
                if readout_settings[key] not in valid_readout_settings[key]:
                    raise KeyError(
                        f"{readout_settings[key]} is not a valid value for {key}. Valid \
                        values are f{valid_readout_settings[key]}"
                    )

    @staticmethod
    def _validate_window_settings(window_settings: dict):

        # Validate values
        for key in window_settings.keys():
            if not isinstance(window_settings[key], int):
                raise KeyError(
                    f"{key} does not have an integer value. All window settings should \
                    be integer values"
                )

    def _validate_channel_settings(self, channels: list):

        valid_channels = set(range(self.board.params["channels"]))

        if not set(channels).issubset(valid_channels):
            raise TypeError(
                f"{channels} is not in range of valid channels for this board model. \
                Valid range is from 0 to {self.board.params['channels']}"
            )


def increase_margin(margin: float, margin_inc: float = 1.5, max_margin: float = 5):
    """Increases the margin, using an exponential standoff"""
    margin *= margin_inc
    margin = min(margin, max_margin)
    return margin


def sleep_calc(board, margin: float = 2.0) -> float:
    """Compute the `sleeptime` for the board.

    Using the `board.params` to gather blocksize, baudrate and readout
    parameters compute the minumum sleep time.

    The `margin` can be dynamically altered as a standoff in case the calc
    doesn't match real transfer rate.
    By increasing `margin` it's possible to increase `sleeptime` in case of
    real-world differences between calculated baudrate and real. Or if
    the return data is longer/padded.

    Args:
        board(naludaq.board)
        margin(float): Multiplier to increase sleeptime due to real-world
            scenarios.

    Returns:
        sleeptime in seconds as a float

    """
    baudrate = board.connection_info.get("speed", 115200)
    transferrate = baudrate // 8
    windows = board.params.get("pedestals_blocks", 16)
    channels = board.params.get("channels", 4)
    samples = board.params.get("samples", 64)
    data = windows * channels * samples * margin * 2  # 16-bits per value
    sleeptime = data / transferrate

    return sleeptime
