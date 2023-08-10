import src.api.api as API
from datetime import datetime


def get_cameras(id: int) -> list:
    response = API.get(f"cameras/node/{id}")
    return response.json()

def log_connection_status(camera_id: int, message: str, date: datetime):
    return API.post(f"cameras/{camera_id}/connection_status", {"message": message, "date": date})
