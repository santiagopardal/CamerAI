import threading
import cv2
from PIL import Image
import datetime
import time
import os


class Frame:
    def __init__(self, frame):
        self._frame = frame
        self._resized_and_grayscale = None

        thread = threading.Thread(target=self.__resize_and_grayscale)
        thread.daemon = False
        thread.start()

        self._time = datetime.datetime.now().time()

        self._resized_and_grayscaled = False

        self._stored = False

    def stored(self) -> bool:
        return self._stored

    def get_resized_and_grayscaled(self):
        i = 0
        while not self._resized_and_grayscaled and i < 100:
            i = i + 1
            time.sleep(0.001)

        if self._resized_and_grayscale is None:
            self.__resize_and_grayscale()
            print("Fuck it,", type(self._resized_and_grayscale))
        return self._resized_and_grayscale

    def store(self, folder):
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