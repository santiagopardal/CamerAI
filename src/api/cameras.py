import src.api.api as API
from datetime import datetime


async def get_cameras() -> list:
    return (await API.get("cameras")).json()


async def log_connection_status(camera_id: int, message: str, date: datetime):
    return await API.post(f"cameras/{camera_id}/connection_status?message={message}&date={date}")
