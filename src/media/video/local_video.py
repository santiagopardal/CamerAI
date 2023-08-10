from .video import Video
from cv2 import VideoCapture
import os


class LocalVideo(Video):
    def __init__(self, id: int, path: str):
        super().__init__(id, path)
        self._video = VideoCapture(self._path)

    def delete(self):
        try:
            os.remove(self._path)
            super().delete()
        except:
            pass
