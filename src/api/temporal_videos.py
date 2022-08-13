import math
from datetime import datetime
import src.api.api as API
from src.utils.date_utils import get_numbers_as_string
import os
import asyncio
import base64


async def get_temporal_videos(camera_id: int, date: datetime) -> list:
    day, month, year = get_numbers_as_string(date)
    temporal_videos_endpoint = "cameras/{}/temporal_videos/{}-{}-{}".format(camera_id, day, month, year)

    return (await API.get(temporal_videos_endpoint)).json()


async def add_temporal_video(camera_id: int, date: datetime, path: str):
    day, month, year = get_numbers_as_string(date)

    api_endpoint = "cameras/{}/temporal_videos/{}-{}-{}".format(camera_id, day, month, year)

    return await API.post(api_endpoint, {"path": path})


async def upload(camera_id: int, date: datetime, path: str):
    day, month, year = get_numbers_as_string(date)

    api_endpoint = "cameras/{}/temporal_videos/{}-{}-{}".format(camera_id, day, month, year)

    with open(path, 'rb') as file:
        await _upload_parts(file, api_endpoint, path)


async def _upload_parts(file, api_endpoint, old_path):
    filename = file.name.split("/")[-1]
    size = os.path.getsize(file.name)
    parts = math.ceil(size / (1024 * 1024))

    requests = [
        API.put(
            api_endpoint,
            {
                "filename": filename,
                "chunk": base64.b64encode(file.read(1024 * 1024)),
                "part": part,
                "parts": parts,
                "old_path": old_path,
                "upload_complete": False
            }
        )
        for part in range(parts)
    ]

    await asyncio.gather(*requests)
    asyncio.create_task(
        API.put(
            api_endpoint,
            {
                "filename": filename,
                "parts": parts,
                "old_path": old_path,
                "upload_complete": True
            }
        )
    )


async def remove_video(id: int):
    api_endpoint = "temporal_videos/{}".format(id)

    return await API.delete(api_endpoint)


async def remove_temporal_videos(camera_id: int, date: datetime):
    day, month, year = get_numbers_as_string(date)
    api_endpoint = "cameras/{}/temporal_videos/{}-{}-{}".format(camera_id, day, month, year)

    return await API.delete(api_endpoint)
