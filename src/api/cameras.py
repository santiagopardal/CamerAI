import src.api.api as api
from datetime import datetime


def get_cameras() -> list:
    return api.get("cameras").json()


def log_connection_status(camera_id: int, message: str, date: datetime):
    return api.post(f"cameras/{camera_id}/connection_status?message={message}&date={date}")
