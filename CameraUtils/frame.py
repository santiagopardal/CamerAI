import cv2
from PIL import Image
import datetime
import os
import numpy as np
import constants


class Frame(object):
    __slots__ = "_time", "_frame", "_resized_and_grayscale", "_stored_in"

    def __init__(self, frame, time=datetime.datetime.now().time()):
        self._time = time
        self._frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self._resized_and_grayscale = None
        self._stored_in = []

    @property
    def frame(self) -> np.ndarray:
        return self._frame

    @property
    def time(self) -> datetime.datetime.time:
        return self._time

    @frame.setter
    def frame(self, frm: np.ndarray):
        self._frame = frm

    @time.setter
    def time(self, tme):
        self._time = tme

    def get_resized_and_grayscaled(self) -> np.ndarray:
        """
        Resizes and grayscales the frame if it has not been already and returns it.
        :return: Frame grayscaled and resized.
        """
        if self._resized_and_grayscale is None:
            self._resized_and_grayscale = cv2.resize(self._frame, constants.RESOLUTION, interpolation=cv2.INTER_AREA)
            self._resized_and_grayscale = cv2.cvtColor(self._resized_and_grayscale, cv2.COLOR_RGB2GRAY)

        return self._resized_and_grayscale

    def store(self, folder: str) -> str:
        """
        Stores the frame in the folder if it has not been stored in that folder already, otherwise it will not store it.
        :param folder: Folder to store frame in.
        :return: Path where the frame has been stored.
        """
        if folder not in self._stored_in:
            return self.__store(folder)

    def __store(self, folder: str) -> str:
        """
        Stores the frame in the folder.
        :param folder: Folder to store the frame in.
        :return: Path where the frame has been stored.
        """
        try:
            filename = str(self._time).replace(":", "-") + ".jpeg"

            pth = constants.STORING_PATH
            for fold in folder.split("/"):
                pth = os.path.join(pth, fold)
                if not os.path.exists(pth):
                    os.mkdir(pth)

            folder = os.path.join(pth, str(datetime.datetime.now().date()))
            file_path = os.path.join(folder, filename)

            if not os.path.exists(folder):
                os.mkdir(folder)

            frame = Image.fromarray(self._frame)
            frame.save(file_path, optimize=True, quality=50)
            frame.close()

            self._stored_in.append(folder)

            return file_path
        except Exception as e:
            print("Error storing image from camera on {}".format(folder))
            print(e)

    def clean_cache(self):
        if self._resized_and_grayscale is not None:
            del self._resized_and_grayscale
