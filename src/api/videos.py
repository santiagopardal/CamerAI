from datetime import datetime
import src.api.api as api
from src.utils.date_utils import get_numbers_as_string


def register_new_video(camera_id: int, date: datetime, video_path: str):
    day, month, year = get_numbers_as_string(date)
    register_new_video_endpoint = "cameras/{}/videos/{}-{}-{}?path={}".format(camera_id, day, month, year, video_path)
    return api.post(register_new_video_endpoint)
