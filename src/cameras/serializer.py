from . import Camera, FI9803PV3, FI89182
from .properties import Properties
from .configurations import Configurations

_classes = {
    "FI89182": FI89182,
    "FI9803PV3": FI9803PV3
}


def deserialize(
        id: int,
        name: str,
        model: str,
        ip: str,
        http_port: int,
        user: str,
        password: str,
        width: int,
        height: int,
        framerate: int,
        recording: bool,
        sensitivity: float,
        streaming_port: int = None
) -> Camera:

    model = _classes[model]

    properties = Properties(
        id=id,
        name=name,
        ip=ip,
        http_port=http_port,
        streaming_port=streaming_port,
        frame_width=width,
        frame_height=height,
        frame_rate=framerate
    )
    configurations = Configurations(sensitivity=sensitivity, recording=recording)

    return model(properties, configurations, user, password)
