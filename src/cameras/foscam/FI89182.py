import urllib
from src.handlers import FrameHandler
from src.cameras.camera import Camera
from src.cameras.retrieval_strategy.retrieval_strategy import RetrievalStrategy
from src.cameras.retrieval_strategy.live_retrieval_strategy import LiveRetrievalStrategy
from src.cameras.properties import Properties
from src.cameras.configurations import Configurations


SNAPSHOT_URL = "http://{}:{}/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr={}&pwd={}"
LIVE_VIDEO_URL = "http://{}:{}/videostream.cgi?user={}&pwd={}"
WIDTH = 640
HEIGHT = 480
FRAME_RATE = 15


class FI89182(Camera):
    def __init__(self, properties: Properties, configurations: Configurations,
                 user: str, password: str, retrieval_strategy: RetrievalStrategy = None,
                 frames_handler: FrameHandler = None
                 ):
        user = urllib.parse.quote(user)
        password = urllib.parse.quote(password)

        video_url = LIVE_VIDEO_URL.format(properties.ip, properties.port, user, password)
        snapshot_url = SNAPSHOT_URL.format(properties.ip, properties.port, user, password)
        retrieval_strategy = retrieval_strategy if retrieval_strategy else LiveRetrievalStrategy(self)

        super().__init__(properties.id, properties.ip, properties.port, video_url, snapshot_url, properties.name, FRAME_RATE, WIDTH, HEIGHT, configurations.sensitivity, retrieval_strategy, frames_handler)

    @classmethod
    def from_json(cls, json: dict) -> Camera:
        json["frame_width"] = WIDTH
        json["frame_height"] = HEIGHT
        json["frame_rate"] = FRAME_RATE

        properties = Properties(**json)
        configurations = Configurations(**json["configurations"])

        instance = cls(properties, configurations, json["user"], json["password"])

        if configurations.recording:
            instance.record()

        return instance

    def __eq__(self, other):
        if isinstance(other, FI89182):
            return super().__eq__(other)

        return False
