from datetime import datetime
import src.api.api as API
from src.utils.date_utils import get_numbers_as_string


def register_new_video(camera_id: int, date: datetime, video_path: str):
    day, month, year = get_numbers_as_string(date)
    register_new_video_endpoint = "cameras/{}/videos/{}-{}-{}".format(camera_id, day, month, year)
    return API.post(register_new_video_endpoint, {"path": video_path})
