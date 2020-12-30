import cv2
from PIL import Image
import datetime
import os
import numpy as np
import Constants


class Frame:
    def __init__(self, frame):
        assert frame is not None
        self._time = datetime.datetime.now().time()

        self._frame = frame

        self._resized_and_grayscale = None

        self._resized_and_grayscaled = False

        self._stored = False
        self._stored_in = []

    def stored(self) -> bool:
        return self._stored

    def set_time(self, tme):
        self._time = tme

    def get_frame(self):
        return self._frame

    def get_time(self):
        return self._time

    def denoise(self):
        self._frame = self.get_denoised_frame()

    def get_denoised_frame(self):
        kernel = np.ones((3, 3), np.float32) / 9
        frm = cv2.filter2D(self._frame, -1, kernel)
        res = Frame(frm)
        res.set_time(self._time)

        return res

    def get_resized_and_grayscaled(self):
        if not self._resized_and_grayscaled:
            self.__resize_and_grayscale()

        return self._resized_and_grayscale

    def store(self, folder: str) -> str:
        if not self._stored:
            return self.__store(folder)
        else:
            if folder not in self._stored_in:
                return self.__store(folder)

    def __store(self, folder: str) -> str:
        try:
            filename = str(self._time).replace(":", "-") + ".jpeg"

            pth = Constants.STORING_PATH
            for fold in folder.split("/"):
                pth = os.path.join(pth, fold)
                if not os.path.exists(pth):
                    os.mkdir(pth)

            folder = os.path.join(pth, str(datetime.datetime.now().date()))
            file_path = os.path.join(folder, filename)

            if not os.path.exists(folder):
                os.mkdir(folder)

            frame = cv2.cvtColor(self._frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)
            frame.save(file_path, optimize=True, quality=50)
            del frame

            self._stored = True
            self._stored_in.append(folder)

            return os.path.join(folder, filename)
        except Exception as e:
            print("Error storing image from camera on {}".format(folder))
            print(e)

    def __resize_and_grayscale(self):
        self._resized_and_grayscale = cv2.resize(self._frame, Constants.RESOLUTION, interpolation=cv2.INTER_AREA)
        self._resized_and_grayscale = cv2.cvtColor(self._resized_and_grayscale, cv2.COLOR_RGB2GRAY)
        self._resized_and_grayscaled = True
