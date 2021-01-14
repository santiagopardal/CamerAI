from Cameras.Camera import Camera, FI89182, FI9803PV3

classes = {
    "FI89182": FI89182,
    "FI9803PV3": FI9803PV3
}


def deserialize(cam: dict) -> Camera:
    model = classes[cam["model"]]

    return model.from_dict(cam)
