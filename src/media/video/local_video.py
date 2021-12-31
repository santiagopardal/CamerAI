from src.media.video.video import Video
from cv2 import VideoCapture


class LocalVideo(Video):
    def __init__(self, path):
        super().__init__(path)
        self._video = VideoCapture(self._path)
