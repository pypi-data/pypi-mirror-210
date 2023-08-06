import logging
import time
from collections import deque

import numpy as np

from naludaq.communication import control_registers, digital_registers
from naludaq.controllers import get_dac_controller
from naludaq.helpers.exceptions import BoardParameterError, PedestalsDataCaptureError
from naludaq.tools.pedestals import get_pedestals_controller

LOGGER = logging.getLogger(__name__)  # pylint: disable=invalid-name
DigitalRegisters = digital_registers.DigitalRegisters
ControlRegisters = control_registers.ControlRegisters


class DACSweepController:
    """DAC Sweep Controller allows the user to easily collect data for
    a sweep of dac values.

    The DAC Sweep Controller uses portions of the pedestal controller
    to collect data for every sample per channel per dac sweep, allowing
    the user to find the linear region and linear regression values on
    a per sample basis.

    Args:
        board (naludaq.board): Board object

    Attributes:
        num_captures_for_peds_avg: How many datapoints/samplepoint used to calculate the average.

    raises:
        BoardParameterError if ext_dac fields are not available amoung the board params.
    """

    def __init__(self, board):
        # The type of daq used depends on the connection type
        self._board = None
        self.board = board
        self.num_evt_per_dacval = 10
        self.dac_max_counts: int = self._get_max_counts()
        self._progress: list = []
        self._cancel = False
        self.ped_ctrl = None
        self._backup_dac: dict = {}

    def _get_max_counts(self) -> int:
        try:
            return self.board.params["ext_dac"]["max_counts"]
        except KeyError as e:
            raise BoardParameterError(
                f"The register file lacks necessary ext_dac fields: {e}"
            )

    @property
    def dac_max_counts(self):
        """Get/Set the max count value for the DAC.

        The true max value is determined by the board params.

        12-bit: <= 4095
        16-bit: <= 65535

        Raises:
            TypeError: if value is not an int
            ValueError: if value is outside of the boards accepted range.
        """
        return self._dac_max_counts

    @dac_max_counts.setter
    def dac_max_counts(self, value):
        if not isinstance(value, int):
            raise TypeError("dac max counts must be an int.")
        min_val = self.board.params["ext_dac"].get("min_counts", 0)
        max_val = self.board.params["ext_dac"].get("max_counts", 4095)
        if not 0 < value <= max_val:
            ValueError(
                f"dac_max_counts must be a value between {min_val} and {max_val}"
            )
        self._dac_max_counts = value

    @property
    def board(self):
        return self._board

    @board.setter
    def board(self, board):
        self._board = board

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        if not hasattr(value, "append"):
            raise TypeError("Progress is stored in a list")
        self._progress = value

    def cancel(self):
        """Cancels the dac sweep as soon as possible.
        No data is generated, and the board is restored to
        its previous state.

        Can only be called from a separate thread.
        """
        self._cancel = True
        if self.ped_ctrl:
            self.ped_ctrl.cancel()

    def dac_sweep(
        self,
        step_size: int = 50,
        min_counts: int = 0,
        max_counts: int = None,
        events_per_datapt: int = 10,
        channels: list = None,
    ):
        """Perform a dac sweep with a given step size.
        IMPORTANT: TURN OFF CONNECTED FUNCTION GENERATORS BEFORE RUNNING
        Ext-dac + signal = :(

            Args:
                step_size (int): Step sizes for the ext-dac, from 0 to max_counts

            Returns:
                dac_sweep (dict): In form dac_sweep[Dac Val][Block #][Event #] or None
                    if the dac sweep was canceled.
                min_counts (int): minimum DAC value to start sweep from
                max_counts (int): maximum DAC value to stop sweep at
                events_per_datapt (int): number of events per data point
                channels (list): list of channel numbers to sweep over
        """
        self._cancel = False

        if step_size <= 0 or step_size > self.dac_max_counts:
            raise ValueError(f"Step size is out of bounds: 0-{self.dac_max_counts}")
        if channels is None:
            channels = list(range(self.board.channels))
        if max_counts is None:
            max_counts = self.board.params["ext_dac"]["max_counts"]

        self._backup_dac_values()

        output2analyze = {}

        ext_dac_values = np.arange(min_counts, max_counts + 1, step_size)
        LOGGER.info(
            f"Starting DAC Sweep from {min_counts}-{self.dac_max_counts} with step {step_size}"
        )

        for dac_idx, dac_val in enumerate(ext_dac_values):
            dac_val = int(dac_val)
            LOGGER.info(f"Currently running DAC_val: {dac_val}")
            # set dac value for all channels
            self.progress.append(
                (
                    int(98 * (dac_val - min_counts) / (max_counts - min_counts)),
                    f"Collecting DAC value {dac_idx+1}/{len(ext_dac_values)}",
                )
            )
            get_dac_controller(self.board).set_dacs(dac_val, channels)
            time.sleep(0.001)
            data2analyze = deque()
            try:
                self.ped_ctrl = get_pedestals_controller(self.board, channels=channels)
                self.ped_ctrl._capture_data_for_pedestals(events_per_datapt)
                data2analyze = self.ped_ctrl.validated_blocks
            except PedestalsDataCaptureError:
                LOGGER.error("Couldn't capture DAC data")

            # Readout data for all channels, all windows.
            output2analyze[dac_val] = data2analyze
            LOGGER.info(f"{dac_val} total data: {len(data2analyze)}")

            if self._cancel:
                break

        # Restore backups
        self._restore_dac_backup()

        # Data is probably bad if canceled, so return None
        if self._cancel:
            return None

        # save data
        try:
            self.progress.append((99, "Saving DAC Sweep"))
        except:
            LOGGER.debug("Status message couldn't append to self.progress")
        return output2analyze

    def _backup_dac_values(self):
        """Backup the old dac values during sweep"""
        self._backup_dac = (
            self.board.params.get("ext_dac", {}).get("channels", {}).copy()
        )

    def _restore_dac_backup(self):
        for chan, value in self._backup_dac.items():
            get_dac_controller(self.board).set_single_dac(chan, value)
