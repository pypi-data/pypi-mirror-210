import itertools
import time
from collections import deque

import numpy as np

from naludaq.backend import AcquisitionManager, ConnectionManager
from naludaq.communication import AnalogRegisters
from naludaq.controllers import (
    get_board_controller,
    get_dac_controller,
    get_readout_controller,
)
from naludaq.daq.workers.packager import get_packager
from naludaq.daq.workers.worker_serial_reader import SerialReader
from naludaq.helpers import event_transfer_time
from naludaq.helpers.exceptions import BadDataError
from naludaq.parsers import get_parser
from naludaq.tools import EventWaiter

from .bayesian_optimizer import BayesianOptimizer


class GainStageTuner(BayesianOptimizer):
    def __init__(self, board, bounds, score_function=None):

        if score_function is None:
            score_function = self.calculate_mean_diff_from_acq

        self.score_function = score_function
        self.cost_function = self.score_variable_pair
        super().__init__(board, self.cost_function, bounds)
        self.board = board
        self.bounds = bounds

        self.events_per_probe = 10
        self.readout_params = {"trig": "imm", "lb": "forced"}

        self.event_params = {
            "windows": 10,
            "lookback": 20,
            "write_after_trig": 254,
        }

    def run(self, n_iter=50):
        results = self.maximize(n_iter)

        suggested_isel = round(results["params"]["y"])
        suggested_dac = round(results["params"]["x"])

        AnalogRegisters(self.board).write("isel", suggested_isel)
        get_dac_controller(self.board).set_dacs(suggested_dac)

    def score_variable_pair(self, x: int, y: int) -> float:
        """Sets the ISEL and DAC value to a certain value on the board, then captures some pedestals
        data and scores the data capture based on how close the average value is to midrange. The
        higher the value, the closer all 4 channels are to being averaged around 2048.

        Args:
            x (int): DAC Value. HAS to be named x since that is the kwarg name that bayes_opt module uses
            y (int): ISEL Value. HAS to be named y since that is the kwarg name that bayes_opt module uses

        Returns:
            float: Score based on how close all channel averages are to midrange. Higher the number,
                closer the value is to midrange
        """
        x = round(x)
        y = round(y)

        # Apply parameters
        AnalogRegisters(self.board).write("isel", y)
        get_dac_controller(self.board).set_dacs(x)

        # Get Data
        acq = self._get_data()

        # Calculate Score
        score = self.score_function(acq)

        return score

    def _get_data(self):

        data = self._protected_readout()
        return data

    def _readout_packages(self, timeout: int = 5) -> deque:

        if self.board.using_new_backend:
            return self._backend_readout(timeout)

        return self._classic_readout(timeout)

    def _classic_readout(self, timeout: int = 5) -> deque:
        """Basic readout function based on naludaq's example script for acquiring waveform data.

        Args:
            board (Board): board object with active connection
            trig (str, optional): trigger type. Defaults to 'imm'.
            lb (str, optional): lookback type. Defaults to 'forced'.
            timeout (int, optional): max amt of time to wait for evt data (seconds). Defaults to 5.

        Returns:
            deque: deque of raw captured waveform data, in bytearrays
        """

        serial_buffer = deque()
        output_buffer = deque()
        evt_waiter = EventWaiter(output_buffer, self.events_per_probe, timeout=timeout)

        stopword = self.board.params["stop_word"]
        sr = SerialReader(self.board.connection, serial_buffer)
        pk = get_packager(
            self.board, serial_buffer, output_buffer, deque(), stopword, 100
        )

        while self.board.connection.in_waiting:
            self.board.connection.reset_input_buffer()

        _bc = get_board_controller(self.board)

        _bc.start_readout(
            trig=self.readout_params["trig"],
            lb=self.readout_params["lb"],
            singleEv=True,
        )
        pk.start()
        sr.start()

        evt_waiter.start()

        sr.stop()
        pk.stop()
        _bc.stop_readout()

        return output_buffer

    def _backend_readout(self, timeout: int = 5) -> deque:
        """
        Backend readout function for acquiring waveform data using NaluDaq's Rust Backend.
        Incompatible with the old way of reading out (anything that has "get_x_connection")

        Args:
            timeout (int, optional): max amt of time to wait for evt data (seconds). Defaults to 5.

        Returns:
            deque: deque of raw captured waveform data, in bytearrays
        """

        output_buffer = deque()
        timeout = timeout / self.events_per_probe

        _bc = get_board_controller(self.board)

        # Clears the I/O buffers for whatever connection thats being used
        ConnectionManager(self.board).device.clear_buffers()

        _bc.start_readout(
            trig=self.readout_params["trig"],
            lb=self.readout_params["lb"],
            singleEv=True,
        )

        # use a temporary acquisition to stream data into an output buffer
        try:
            with AcquisitionManager(self.board).create_temporary() as acq:
                acq.set_output()
                stream = acq.stream(timeout=timeout)

                output_buffer.extend(itertools.islice(stream, self.events_per_probe))

        except TimeoutError:
            raise BadDataError

        _bc.stop_readout()

        return output_buffer

    def _configure_readout(self) -> None:
        """Prepares the board with the proper readout parameters. To be used BEFORE readout.

        Args:
            board (board): board with active connection
            windows (int): number of windows to capture per trigger
            lookback (int): pre-trigger length (in windows)
            write_after_trig (int): record length (in windows)
            events (int): number of trigger events to capture

        """
        _rc = get_readout_controller(self.board)
        _rc.number_events_to_read(self.events_per_probe)
        _rc.set_readout_channels(list(range(self.board.params["channels"])))
        _rc.set_read_window(**self.event_params)

    def _protected_readout(self) -> list:
        """I needed a function that is protected against BadDataError raises, which occur presumably
        because my wait time is too short. I don't know the exact reason, but trying again over and over
        seems to work so I'm sticking with it for now.

        Args:
            board (Board): board object with active connection
            trig_type (str): trigger type of acquisition
            lb_type (str): lookback type of acquisition
            events (int): number of events to capture (1 trigger = 1 event)

        Returns:
            pdata (list): list of parsed events
        """

        self._configure_readout()

        pdata = []
        fails = 0
        delay_per_evt = event_transfer_time(
            self.board, windows=self.event_params["windows"], overhead=0.5
        )
        delay = delay_per_evt * self.events_per_probe

        parser = get_parser(self.board.params)

        while len(pdata) == 0 and fails < 5:
            try:
                data = self._readout_packages(timeout=delay)
                pdata = [parser.parse(evt) for evt in data]
                _ = [self._verify_evt_or_raise(evt) for evt in pdata]
            except BadDataError:
                print(f"Bad Data Error: Fails: {fails}")
                time.sleep(1)  # give the board some time to get its shit together
                fails += 1

        if fails >= 5:
            print("Tried 5 times. Failed. Giving Up")
            return 0

        return pdata

    def calculate_mean_diff_from_acq(self, acq):
        """Calculates the difference from the acq's average to midrange (2048)."""

        evt_averages = []

        for evt in acq:
            evt_averages.append([np.mean(chandata) for chandata in evt["data"]])

        chan_averages = np.mean(evt_averages, axis=0)

        # compute score (also known as the cost function)
        cost_value = 0 - np.sum([np.abs(avg - 2048) for avg in chan_averages])

        return cost_value

    def _verify_evt_or_raise(self, evt):

        if type(evt) is not dict:
            raise BadDataError("evt is not dictionary")

        if "data" not in evt.keys():
            raise BadDataError("evt does not have 'data' field")

        if evt["data"].dtype not in ["uint16", "uint32"]:
            raise BadDataError(f"evt data is wrong type: {evt['data'].dtype}")
