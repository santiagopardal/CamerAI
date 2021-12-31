from cv2 import VideoCapture, CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT, CAP_PROP_FPS


class Video:
    _video: VideoCapture

    def __init__(self, path):
        self._path = path

    def __iter__(self):
        while self._video.isOpened():
            _, frame = self._video.read()
            yield frame

        self._video.release()

    @property
    def width(self):
        return int(self._video.get(CAP_PROP_FRAME_WIDTH))

    @property
    def height(self):
        return int(self._video.get(CAP_PROP_FRAME_HEIGHT))

    @property
    def frame_rate(self):
        return self._video.get(CAP_PROP_FPS)
