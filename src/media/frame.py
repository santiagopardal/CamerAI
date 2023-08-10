from datetime import datetime
import numpy as np


class Frame(object):
    __slots__ = "_date", "_frame"

    def __init__(self, frame, date=datetime.now()):
        self._date = date
        self._frame = frame

    @property
    def frame(self) -> np.ndarray:
        return self._frame

    @property
    def date(self) -> datetime:
        return self._date

    @property
    def time(self) -> datetime.time:
        return self._date.time()

    @frame.setter
    def frame(self, frm: np.ndarray):
        self._frame = frm
