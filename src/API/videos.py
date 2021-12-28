import requests
from src.constants import API_URL
from datetime import datetime
from src.date_helper import get_numbers_as_string


def register_new_video(camera_id: int, date: datetime, video_path: str):
    day, month, year = get_numbers_as_string(date)
    register_new_video_endpoint = "{}/videos/{}/{}-{}-{}?path={}".format(API_URL, camera_id,
                                                                         day, month, year,
                                                                         video_path)
    requests.post(register_new_video_endpoint)
