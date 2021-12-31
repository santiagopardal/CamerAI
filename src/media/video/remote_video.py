from src.media.video.video import Video
from cv2 import VideoCapture


class RemoteVideo(Video):
    def __init__(self, path, stream_endpoint):
        super().__init__(path)
        self._video = VideoCapture(stream_endpoint)
