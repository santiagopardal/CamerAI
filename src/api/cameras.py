import src.api.api as API
from src.cameras.serializer import deserialize
from datetime import datetime


async def get_cameras(id: int) -> list:
    response = await API.get(f"cameras/node/{id}")
    cameras_as_json = response.json()
    return [deserialize(camera) for camera in cameras_as_json]

async def log_connection_status(camera_id: int, message: str, date: datetime):
    return await API.post(f"cameras/{camera_id}/connection_status", {"message": message, "date": date})
