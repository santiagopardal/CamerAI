from . import Camera, FI9803PV3, FI89182

_classes = {
    "FI89182": FI89182,
    "FI9803PV3": FI9803PV3
}


def deserialize(cam: dict) -> Camera:
    model = _classes[cam["model"]]

    return model.from_json(cam)
