import math
from datetime import datetime
import src.api.api as API
from src.utils.date_utils import get_numbers_as_string
import os
import base64


def get_temporal_videos(camera_id: int, date: datetime) -> list:
    day, month, year = get_numbers_as_string(date)
    temporal_videos_endpoint = "cameras/{}/temporal_videos/{}-{}-{}".format(camera_id, day, month, year)

    return API.get(temporal_videos_endpoint).json()


def add_temporal_video(camera_id: int, date: datetime, path: str):
    day, month, year = get_numbers_as_string(date)

    api_endpoint = "cameras/{}/temporal_videos/{}-{}-{}?path={}".format(camera_id, day, month, year, path)

    return API.post(api_endpoint)


def upload(camera_id: int, date: datetime, path: str):
    day, month, year = get_numbers_as_string(date)

    api_endpoint = "cameras/{}/temporal_videos/{}-{}-{}?old_path={}".format(camera_id, day, month, year, path)

    with open(path, 'rb') as file:
        _upload_parts(file, api_endpoint)


def _upload_parts(file, api_endpoint):
    filename = file.name.split("/")[-1]
    size = os.path.getsize(file.name)
    parts = math.ceil(size / (1024 * 1024))

    for part in range(parts):
        chunk = file.read(1024 * 1024)
        chunk = base64.b64encode(chunk)

        API.put(api_endpoint, {"filename": filename, "chunk": chunk, "part": part, "parts": parts})


def remove_video(id: int):
    api_endpoint = "temporal_videos/{}".format(id)

    return API.delete(api_endpoint)


def remove_temporal_videos(camera_id: int, date: datetime):
    day, month, year = get_numbers_as_string(date)
    api_endpoint = "cameras/{}/temporal_videos/{}-{}-{}".format(camera_id, day, month, year)

    return API.delete(api_endpoint)
