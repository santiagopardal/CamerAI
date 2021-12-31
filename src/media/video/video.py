from cv2 import VideoCapture


class Video:
    _video: VideoCapture

    def __init__(self, path):
        self._path = path

    def __iter__(self):
        while self._video.isOpened():
            _, frame = self._video.read()
            yield frame

        self._video.release()
