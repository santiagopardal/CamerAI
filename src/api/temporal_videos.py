from datetime import datetime
import src.api.api as API
from src.utils.date_utils import get_numbers_as_string


def add_temporal_video(camera_id: int, date: datetime, path: str):
    day, month, year = get_numbers_as_string(date)

    api_endpoint = "cameras/{}/temporal_videos/{}-{}-{}".format(camera_id, day, month, year)

    return API.post(api_endpoint, {"path": path})


def remove_video(id: int):
    api_endpoint = "temporal_videos/{}".format(id)
    return API.delete(api_endpoint)


def remove_temporal_videos(camera_id: int, date: datetime):
    day, month, year = get_numbers_as_string(date)
    api_endpoint = "cameras/{}/temporal_videos/{}-{}-{}".format(camera_id, day, month, year)
    return API.delete(api_endpoint)
