import math
from datetime import datetime
import src.api.api as API
from src.utils.date_utils import get_numbers_as_string
import os
import base64


def get_temporal_videos(camera_id: int, date: datetime) -> list:
    day, month, year = get_numbers_as_string(date)
    temporal_videos_endpoint = "cameras/{}/temporal_videos/{}-{}-{}".format(camera_id, day, month, year)
    response = API.get(temporal_videos_endpoint)
    return response.json()


def add_temporal_video(camera_id: int, date: datetime, path: str):
    day, month, year = get_numbers_as_string(date)

    api_endpoint = "cameras/{}/temporal_videos/{}-{}-{}".format(camera_id, day, month, year)

    return API.post(api_endpoint, {"path": path})


def upload(camera_id: int, date: datetime, path: str):
    day, month, year = get_numbers_as_string(date)

    api_endpoint = "cameras/{}/temporal_videos/{}-{}-{}".format(camera_id, day, month, year)

    with open(path, 'rb') as file:
        _upload_parts(file, api_endpoint, path)


def _upload_parts(file, api_endpoint, old_path):
    filename = file.name.split("/")[-1]
    size = os.path.getsize(file.name)
    parts = math.ceil(size / (1024 * 1024))

    for part in range(parts):
        body = {
            "filename": filename,
            "chunk": base64.b64encode(file.read(1024 * 1024)),
            "part": part,
            "parts": parts,
            "old_path": old_path,
            "upload_complete": False
        }
        API.put(api_endpoint, body)

    API.put(
        api_endpoint,
        {
            "filename": filename,
            "parts": parts,
            "old_path": old_path,
            "upload_complete": True
        }
    )


def remove_video(id: int):
    api_endpoint = "temporal_videos/{}".format(id)
    return API.delete(api_endpoint)


def remove_temporal_videos(camera_id: int, date: datetime):
    day, month, year = get_numbers_as_string(date)
    api_endpoint = "cameras/{}/temporal_videos/{}-{}-{}".format(camera_id, day, month, year)
    return API.delete(api_endpoint)
