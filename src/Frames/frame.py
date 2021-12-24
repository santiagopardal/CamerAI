import cv2
import datetime
import os
import numpy as np
from src import constants


class Frame(object):
    __slots__ = "_date", "_frame", "_resized_and_grayscale", "_stored_in"

    def __init__(self, frame, date=datetime.datetime.now()):
        self._date = date
        self._frame = frame
        self._resized_and_grayscale = None
        self._stored_in = []

    @property
    def frame(self) -> np.ndarray:
        return self._frame

    @property
    def date(self) -> datetime.datetime:
        return self._date

    @property
    def time(self) -> datetime.datetime.time:
        return self._date.time()

    @frame.setter
    def frame(self, frm: np.ndarray):
        self._frame = frm

    def get_resized_and_grayscaled(self) -> np.ndarray:
        """
        Resizes and grayscales the frame if it has not been already and returns it.
        :return: Frame grayscaled and resized.
        """
        if self._resized_and_grayscale is None:
            self._resized_and_grayscale = cv2.resize(self._frame, constants.RESOLUTION, interpolation=cv2.INTER_AREA)
            self._resized_and_grayscale = cv2.cvtColor(self._resized_and_grayscale, cv2.COLOR_RGB2GRAY)

        return self._resized_and_grayscale

    def clean_cache(self):
        if self._resized_and_grayscale is not None:
            del self._resized_and_grayscale
