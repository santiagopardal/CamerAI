import urllib
from src.handlers.frame_handler import FrameHandler
from src.cameras.camera import Camera
from src.cameras.retrieval_strategy.retrieval_strategy import RetrievalStrategy
from src.cameras.retrieval_strategy.live_retrieval_strategy import LiveRetrievalStrategy


SCREENSHOT_URL = "http://{}:{}/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr={}&pwd={}"
LIVE_VIDEO_URL = "http://{}:{}/videostream.cgi?user={}&pwd={}"
WIDTH = 640
HEIGHT = 480
FRAME_RATE = 15


class FI89182(Camera):
    def __init__(self, id: int, ip: str, port: int, place: str,
                 user: str, password: str,
                 retrieval_strategy: RetrievalStrategy = None, frames_handler: FrameHandler = None):
        """
        :param ip: IP where the camera is located.
        :param port: Port to connect to camera.
        :param place: Place where the camera is located.
        :param user: Username to connect.
        :param password: Password.
        :param frames_handler: Handler to handle new frames, if set to None will use default.
        """
        user = urllib.parse.quote(user)
        password = urllib.parse.quote(password)

        live_video_url = LIVE_VIDEO_URL.format(ip, port, user, password)
        retrieval_strategy = retrieval_strategy if retrieval_strategy \
            else LiveRetrievalStrategy(live_video_url, FRAME_RATE, WIDTH, HEIGHT)

        super().__init__(id, ip, port, place, FRAME_RATE, retrieval_strategy, frames_handler)

    @classmethod
    def from_json(cls, json: dict) -> Camera:
        """
        Returns a Camera from a dictionary.
        :param json: Dictionary to transform into FI89182 camera.
        :return: FI89182 camera from the dictionary.
        """
        return cls(json["id"], json["ip"], json["http_port"], json["name"], json["user"], json["password"])

    def __eq__(self, other):
        if isinstance(other, FI89182):
            return super().__eq__(other)

        return False
