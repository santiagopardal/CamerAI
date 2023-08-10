from .video import Video
from cv2 import VideoCapture


class RemoteVideo(Video):
    def __init__(self, id: int, path: str, stream_endpoint: str):
        super().__init__(id, path)
        self._video = VideoCapture(stream_endpoint)
