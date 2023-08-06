import logging
from typing import Iterator

from naludaq.backend.models.acquisition import RemoteAcquisition
from naludaq.controllers.board import get_board_controller

from .default import PedestalsGeneratorNew

LOGGER = logging.getLogger(
    "naludaq.pedestals_controller_aav3_new"
)  # pylint: disable=invalid-name


class PedestalsGeneratorAardvarcv3New(PedestalsGeneratorNew):
    def _start_readout(self):
        """Start a readout"""
        readout_settings = {
            "trig": "ext",
            "lb": "forced",
            "acq": "pedsub",
            "dig_head": False,
            "ped": "zero",
            "readoutEn": True,
            "singleEv": False,
        }
        get_board_controller(self.board).start_readout(**readout_settings)

    def _stream_valid_events(
        self,
        acq: RemoteAcquisition,
        start: int,
        expected_block: list[int],
    ) -> Iterator[dict]:
        """A generator for validated events.

        Args:
            acq (RemoteAcquisition): the acquisition
            count (int): number of events to stream
            start (int): start event in the acquisition
            expected_block (list[int]): expected window labels
        """
        bc = get_board_controller(self.board)
        bc.toggle_trigger()
        for event in super()._stream_valid_events(acq, start, expected_block):
            yield event
            bc.toggle_trigger()
