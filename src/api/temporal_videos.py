import requests
from src.constants import API_URL
from datetime import datetime
from src.utils.date_utils import get_numbers_as_string


def get_temporal_videos(camera_id: int, date: datetime) -> list:
    day, month, year = get_numbers_as_string(date)
    temporal_videos_endpoint = "{}/temporal_videos/{}/{}-{}-{}".format(API_URL, camera_id, day, month, year)
    return requests.get(temporal_videos_endpoint).json()


def add_temporal_video(camera_id: int, date: datetime, path: str):
    day, month, year = get_numbers_as_string(date)
    api_endpoint = "{}/temporal_videos/{}/{}-{}-{}?path={}".format(API_URL, camera_id, day, month, year, path)
    requests.post(api_endpoint)


def remove_temporal_videos(camera_id: int, date: datetime):
    day, month, year = get_numbers_as_string(date)
    api_endpoint = "{}/temporal_videos/{}/{}-{}-{}".format(API_URL, camera_id, day, month, year)
    requests.delete(api_endpoint)
