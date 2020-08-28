import cv2
from PIL import Image
import datetime
import os
import numpy as np


class Frame:
    def __init__(self, frame):
        assert frame is not None

        self._frame = frame
        self._resized_and_grayscale = None

        self._time = datetime.datetime.now().time()

        self._resized_and_grayscaled = False

        self._stored = False

    def stored(self) -> bool:
        return self._stored

    def set_time(self, tme):
        self._time = tme

    def get_frame(self):
        return self._frame

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

    def store(self, folder: str):
        if not self._stored:
            try:
                filename = str(self._time).replace(":", "-") + ".jpeg"

                if not os.path.exists(folder):
                    os.mkdir(folder)

                folder = folder + str(datetime.datetime.now().date()) + "/"

                if not os.path.exists(folder):
                    os.mkdir(folder)

                frame = cv2.cvtColor(self._frame, cv2.COLOR_BGR2RGB)
                frame = Image.fromarray(frame)
                frame.save(folder + filename, optimize=True, quality=50)
                del frame

                self._stored = True
            except Exception as e:
                print("Error storing image from camera on {}".format(folder))
                print(e)

    def __resize_and_grayscale(self):
        self._resized_and_grayscale = cv2.resize(self._frame, (256, 144), interpolation=cv2.INTER_AREA)
        self._resized_and_grayscale = cv2.cvtColor(self._resized_and_grayscale, cv2.COLOR_RGB2GRAY)
        self._resized_and_grayscaled = True