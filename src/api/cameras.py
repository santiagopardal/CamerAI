import src.api.api as api


def get_cameras() -> list:
    return api.get("cameras").json()
