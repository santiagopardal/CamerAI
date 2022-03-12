import urllib
from src.handlers.frame_handler import FrameHandler
from src.cameras.camera import Camera
from src.cameras.retrieval_strategy.retrieval_strategy import RetrievalStrategy
from src.cameras.retrieval_strategy.live_retrieval_strategy import LiveRetrievalStrategy


SCREENSHOT_URL = "http://{}:{}/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr={}&pwd={}"
LIVE_VIDEO_URL = "rtsp://{}:{}@{}:{}/videoMain"
WIDTH = 1280
HEIGHT = 720
FRAME_RATE = 23


class FI9803PV3(Camera):
    def __init__(self, id: int, ip: str, port: int, streaming_port: int,
                 name: str, user: str, password: str,
                 retrieval_strategy: RetrievalStrategy = None, frames_handler: FrameHandler = None):
        """
        :param ip: IP where the camera is located.
        :param port: Port to connect to camera.
        :param streaming_port: Port to receive live video.
        :param name: name where the camera is located.
        :param user: Username to connect.
        :param password: Password.
        :param frames_handler: Handler to handle new frames, if set to None will use default.
        """
        user = urllib.parse.quote(user)
        password = urllib.parse.quote(password)

        live_video_url = LIVE_VIDEO_URL.format(user, password, ip, streaming_port)
        retrieval_strategy = retrieval_strategy if retrieval_strategy \
            else LiveRetrievalStrategy(live_video_url, FRAME_RATE, WIDTH, HEIGHT)

        super().__init__(id, ip, port, name, FRAME_RATE, retrieval_strategy, frames_handler)

        self._streaming_port = streaming_port

    @classmethod
    def from_json(cls, json: dict) -> Camera:
        """
        Returns a Camera from a dictionary.
        :param json: Dictionary to transform into FI9803PV3 camera.
        :return: FI9803PV3 camera from the dictionary.
        """
        return cls(json["id"], json["ip"], json["http_port"], json["streaming_port"],
                   json["name"], json["user"], json["password"])

    def __eq__(self, other):
        if isinstance(other, FI9803PV3):
            return super().__eq__(other)

        return False
