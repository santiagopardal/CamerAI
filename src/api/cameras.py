import src.api.api as API
from datetime import datetime


async def get_cameras(id: int) -> list:
    return (await API.get(f"cameras/node/{id}")).json()


async def log_connection_status(camera_id: int, message: str, date: datetime):
    return await API.post(f"cameras/{camera_id}/connection_status", {"message": message, "date": date})
