import urllib
from src.Handlers.frame_handler import FrameHandler
from src.CameraUtils.Camera.live_video_camera import LiveVideoCamera
from src.CameraUtils.Camera.camera import Camera


class FI89182(LiveVideoCamera):
    def __init__(self, ip: str, port: int, place: str,
                 user: str, password: str,
                 frames_handler: FrameHandler = None):
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

        screenshot_url = "http://{}:{}/{}".format(ip, str(port), "cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr={}&pwd={}")
        screenshot_url = screenshot_url.format(user, password)

        live_video_url = "http://{}:{}/{}".format(ip, port, "videostream.cgi?user={}&pwd={}")
        live_video_url = live_video_url.format(user, password)

        super().__init__(ip, port, place, screenshot_url, live_video_url, 640, 480, 15, frames_handler)

    @classmethod
    def from_json(cls, json: dict) -> Camera:
        """
        Returns a Camera from a dictionary.
        :param json: Dictionary to transform into FI89182 camera.
        :return: FI89182 camera from the dictionary.
        """
        return cls(json["ip"], json["http_port"], json["name"], json["user"], json["password"])

    def __eq__(self, other):
        if isinstance(other, FI89182):
            return super().__eq__(other)

        return False
