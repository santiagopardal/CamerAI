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

    api_endpoint = "cameras/{}/temporal_videos/{}-{}-{}?path={}".format(camera_id, day, month, year, path)

    return await API.post(api_endpoint)


async def upload(camera_id: int, date: datetime, path: str):
    day, month, year = get_numbers_as_string(date)

    api_endpoint = "cameras/{}/temporal_videos/{}-{}-{}?old_path={}".format(camera_id, day, month, year, path)

    with open(path, 'rb') as file:
        await _upload_parts(file, api_endpoint)


async def _upload_parts(file, api_endpoint):
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
                "parts": parts
            }
        )
        for part in range(parts - 1)
    ]

    await asyncio.gather(*requests)
    await API.put(
        api_endpoint,
        {
            "filename": filename,
            "chunk": base64.b64encode(file.read(1024 * 1024)),
            "part": parts - 1,
            "parts": parts
        }
    )


async def remove_video(id: int):
    api_endpoint = "temporal_videos/{}".format(id)

    return await API.delete(api_endpoint)


async def remove_temporal_videos(camera_id: int, date: datetime):
    day, month, year = get_numbers_as_string(date)
    api_endpoint = "cameras/{}/temporal_videos/{}-{}-{}".format(camera_id, day, month, year)

    return await API.delete(api_endpoint)
