import urllib
from src.Handlers.frame_handler import FrameHandler
from src.CameraUtils.Camera.live_video_camera import LiveVideoCamera
from src.CameraUtils.Camera.camera import Camera


SCREENSHOT_URL = "http://{}:{}/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr={}&pwd={}"
LIVE_VIDEO_URL = "rtsp://{}:{}@{}:{}/videoMain"
WIDTH = 1280
HEIGHT = 720
FRAME_RATE = 23


class FI9803PV3(LiveVideoCamera):
    def __init__(self, ip: str, port: int, streaming_port: int,
                 place: str, user: str, password: str,
                 frames_handler: FrameHandler = None):
        """
        :param ip: IP where the camera is located.
        :param port: Port to connect to camera.
        :param streaming_port: Port to receive live video.
        :param place: Place where the camera is located.
        :param user: Username to connect.
        :param password: Password.
        :param frames_handler: Handler to handle new frames, if set to None will use default.
        """
        user = urllib.parse.quote(user)
        password = urllib.parse.quote(password)

        screenshot_url = SCREENSHOT_URL.format(ip, port, user, password)
        live_video_url = LIVE_VIDEO_URL.format(user, password, ip, streaming_port)

        super().__init__(ip, port, place, screenshot_url, live_video_url,
                         WIDTH, HEIGHT, FRAME_RATE, frames_handler)

        self._streaming_port = streaming_port

    @classmethod
    def from_json(cls, json: dict) -> Camera:
        """
        Returns a Camera from a dictionary.
        :param json: Dictionary to transform into FI9803PV3 camera.
        :return: FI9803PV3 camera from the dictionary.
        """
        return cls(json["ip"], json["http_port"], json["streaming_port"],
                   json["name"], json["user"], json["password"])

    def __eq__(self, other):
        if isinstance(other, FI9803PV3):
            return super().__eq__(other)

        return False
