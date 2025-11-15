import datetime

from numpy import ndarray


class Frame(object):
    __slots__ = "_date", "_frame"

    def __init__(self, frame: ndarray, date=datetime.datetime.now()):
        self._date = date
        self._frame = frame

    @property
    def frame(self) -> ndarray:
        return self._frame

    @property
    def date(self) -> datetime.datetime:
        return self._date

    @property
    def time(self) -> datetime.time:
        return self._date.time()

    @frame.setter
    def frame(self, frm: ndarray):
        self._frame = frm
