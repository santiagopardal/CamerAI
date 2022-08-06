from src.cameras.camera import Camera
from src.cameras.foscam.FI9803PV3 import FI9803PV3
from src.cameras.foscam.FI89182 import FI89182

_classes = {
    "FI89182": FI89182,
    "FI9803PV3": FI9803PV3
}


def deserialize(cam: dict) -> Camera:
    model = _classes[cam["model"]]

    return model.from_json(cam)
