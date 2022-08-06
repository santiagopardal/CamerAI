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
    def __init__(self, id: int, ip: str, port: int, name: str,
                 user: str, password: str,
                 retrieval_strategy: RetrievalStrategy = None, frames_handler: FrameHandler = None):
        user = urllib.parse.quote(user)
        password = urllib.parse.quote(password)

        video_url = LIVE_VIDEO_URL.format(ip, port, user, password)
        retrieval_strategy = retrieval_strategy if retrieval_strategy else LiveRetrievalStrategy(self)

        super().__init__(id, ip, port, video_url, name, FRAME_RATE, WIDTH, HEIGHT, retrieval_strategy, frames_handler)

    @classmethod
    def from_json(cls, json: dict) -> Camera:
        return cls(json["id"], json["ip"], json["http_port"], json["name"], json["user"], json["password"])

    def __eq__(self, other):
        if isinstance(other, FI89182):
            return super().__eq__(other)

        return False
