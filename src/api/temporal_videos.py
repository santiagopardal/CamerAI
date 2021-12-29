import requests
from src.constants import API_URL
from datetime import datetime
from src.utils.date_utils import get_numbers_as_string
import os
import base64


def get_temporal_videos(camera_id: int, date: datetime) -> list:
    day, month, year = get_numbers_as_string(date)
    temporal_videos_endpoint = "{}/temporal_videos/{}/{}-{}-{}".format(API_URL, camera_id, day, month, year)
    return requests.get(temporal_videos_endpoint).json()


def add_temporal_video(camera_id: int, date: datetime, path: str):
    day, month, year = get_numbers_as_string(date)

    api_endpoint = "{}/temporal_videos/{}/{}-{}-{}?path={}".format(API_URL, camera_id, day, month, year, path)
    return requests.post(api_endpoint)


def upload(camera_id: int, date: datetime, path: str):
    day, month, year = get_numbers_as_string(date)

    api_endpoint = "{}/temporal_videos/{}/{}-{}-{}?old_path={}".format(API_URL, camera_id, day, month, year, path)

    filename = path.split("/")[-1]

    with open(path, 'rb') as file:
        size = os.path.getsize(path)
        parts = int(size / (1024 * 1024)) + 1
        for part in range(parts):
            chunk = file.read(1024 * 1024)
            chunk = base64.b64encode(chunk)
            requests.put(api_endpoint, data={"filename": filename, "chunk": chunk, "part": part, "parts": parts})
            part += 1


def remove_temporal_videos(camera_id: int, date: datetime):
    day, month, year = get_numbers_as_string(date)
    api_endpoint = "{}/temporal_videos/{}/{}-{}-{}".format(API_URL, camera_id, day, month, year)
    return requests.delete(api_endpoint)
