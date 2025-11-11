from datetime import datetime
import src.api.api as API


def add_temporal_video(camera_id: int, date: datetime, path: str):
    api_endpoint = f"cameras/{camera_id}/temporal_videos"

    body = {"path": path, "dateTimestamp": date.timestamp()}

    return API.post(api_endpoint, body)
