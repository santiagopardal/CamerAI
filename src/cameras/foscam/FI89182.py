import urllib
from src.cameras.camera import Camera
from src.cameras.properties import Properties
from src.cameras.configurations import Configurations


SNAPSHOT_URL = "http://{}:{}/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr={}&pwd={}"
LIVE_VIDEO_URL = "http://{}:{}/videostream.cgi?user={}&pwd={}"
WIDTH = 640
HEIGHT = 480
FRAME_RATE = 15


class FI89182(Camera):
    def __init__(
        self, properties: Properties, configurations: Configurations,
        user: str, password: str
    ):
        user = urllib.parse.quote(user)
        password = urllib.parse.quote(password)

        video_url = LIVE_VIDEO_URL.format(properties.ip, properties.port, user, password)
        snapshot_url = SNAPSHOT_URL.format(properties.ip, properties.port, user, password)

        super().__init__(properties, configurations, video_url, snapshot_url)

    def __hash__(self):
        return hash(f"{self.ip}:{self.port}@{self.name}")

    def __eq__(self, other):
        if isinstance(other, FI89182):
            return super().__eq__(other)

        return False
