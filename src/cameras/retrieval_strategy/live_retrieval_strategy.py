from src.cameras.retrieval_strategy.retrieval_strategy import RetrievalStrategy
from cv2 import VideoCapture, CAP_PROP_FPS, CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT, CAP_PROP_BUFFERSIZE, CAP_FFMPEG
from numpy import ndarray
from time import sleep


class LiveRetrievalStrategy(RetrievalStrategy):

    _live_video: VideoCapture
    _url: str
    _frame_rate: int
    _frame_width: int
    _frame_height: int

    def __init__(self, url: str, frame_rate: int, frame_width: int, frame_height: int):
        self._url = url
        self._frame_rate = frame_rate
        self._frame_width = frame_width
        self._frame_height = frame_height
        self._live_video = None

    def connect(self):
        connected = False
        i = 0
        while not connected:
            try:
                if self._live_video:
                    self._live_video.release()

                self._live_video = VideoCapture(self._url, CAP_FFMPEG)
                self._live_video.set(CAP_PROP_FPS, self._frame_rate)
                self._live_video.set(CAP_PROP_FRAME_WIDTH, self._frame_width)
                self._live_video.set(CAP_PROP_FRAME_HEIGHT, self._frame_height)
                self._live_video.set(CAP_PROP_BUFFERSIZE, 3)

                connected = True
            except Exception as e:
                if i < 6:
                    i += 1
                seconds = 2 ** i
                print(e)
                print("Could not connect, retrying in {} seconds".format(seconds))
                sleep(seconds)

        print("Connected!")

    def retrieve(self) -> ndarray:
        grabbed, frame = self._live_video.read()

        while not grabbed:
            print("Reconnecting!")
            self.connect()
            grabbed, frame = self._live_video.read()

        return frame

    def disconnect(self):
        if self._live_video:
            self._live_video.release()
            del self._live_video
