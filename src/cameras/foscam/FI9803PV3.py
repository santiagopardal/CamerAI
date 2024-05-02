import urllib
from src.cameras.camera import Camera
from src.cameras.properties import Properties
from src.cameras.configurations import Configurations


SNAPSHOT_URL = "http://{}:{}/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr={}&pwd={}"
LIVE_VIDEO_URL = "rtsp://{}:{}@{}:{}/videoMain"
WIDTH = 1280
HEIGHT = 720
FRAME_RATE = 23


class FI9803PV3(Camera):
    def __init__(
        self, properties: Properties, configurations: Configurations, user: str,
        password: str
    ):
        user = urllib.parse.quote(user)
        password = urllib.parse.quote(password)

        video_url = LIVE_VIDEO_URL.format(user, password, properties.ip, properties.streaming_port)
        snapshot_url = SNAPSHOT_URL.format(properties.ip, properties.port, user, password)

        super().__init__(properties, configurations, video_url, snapshot_url)

    def __hash__(self):
        return hash(f"{self.ip}:{self.port}@{self.name}")

    def __eq__(self, other):
        if isinstance(other, FI9803PV3):
            return super().__eq__(other)

        return False
