from CameraUtils.Camera.camera import Camera
from CameraUtils.Camera.Foscam.FI9803PV3 import FI9803PV3
from CameraUtils.Camera.Foscam.FI89182 import FI89182

_classes = {
    "FI89182": FI89182,
    "FI9803PV3": FI9803PV3
}


def deserialize(cam: dict) -> Camera:
    """
    Deserializes a camera from a dictionary.
    :return: Camera deserialized.
    """
    model = _classes[cam["model"]]

    return model.from_dict(cam)
