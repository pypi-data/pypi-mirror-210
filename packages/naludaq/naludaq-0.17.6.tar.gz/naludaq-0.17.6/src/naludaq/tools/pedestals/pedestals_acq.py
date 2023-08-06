"""A special data class that behaves like a list but pedestals correct on access."""

from collections import deque

from .pedestals_correcter import PedestalsCorrecter


class PedestalsAcq:
    def __init__(self, pedestals, acquisition=None):
        self.pedestals = pedestals
        self.pedestals_correcter = PedestalsCorrecter(pedestals)
        self.acquisition = acquisition

    def __getitem__(self, index):

        if isinstance(index, slice):
            # Get a slice from the deque
            # use itertools?
            # pedestals correct each
            ped_acq = deque()
            for ev in acq_slice:
                self.pedestals_correcter.run(ev)
            return ped_acq

        elif isinstance(index, int):
            event = self.acquisition[index]
            self.pedestals_correcter.run(event)
            return self.pedestals[index]
