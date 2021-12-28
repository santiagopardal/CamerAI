import os
from datetime import datetime
import cv2
from src.media.savers.media_saver import MediaSaver
from src.media.frame import Frame
from src.constants import STORING_PATH


class LocalFrameSaver(MediaSaver):
    def __init__(self, folder: str):
        self._folder = folder

    def save(self, frame: Frame):
        """
        Stores the frame in the folder.
        :return: Path where the frame has been stored.
        """
        try:
            filename = "{}.jpeg".format(str(frame.time).replace(":", "-"))

            pth = STORING_PATH
            for fold in self._folder.split("/"):
                pth = os.path.join(pth, fold)
                if not os.path.exists(pth):
                    os.mkdir(pth)

            folder = os.path.join(pth, str(datetime.now().date()))
            file_path = os.path.join(folder, filename)

            if not os.path.exists(folder):
                os.mkdir(folder)

            cv2.imwrite(filename=file_path, img=frame.frame)

            return file_path
        except Exception as e:
            print("Error storing image from camera on {}".format(self._folder))
            print(e)
