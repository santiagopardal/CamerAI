import requests
from src.constants import API_URL
import asyncio


NODE = None


def _get_headers():
    global NODE
    if NODE and NODE.id:
        return {"node_id": str(NODE.id)}

    return None


async def get(endpoint: str):
    api_endpoint = "{}/{}".format(API_URL, endpoint)

    for i in range(6):
        try:
            return await asyncio.to_thread(requests.get, api_endpoint, headers=_get_headers())
        except Exception as e:
            if i == 5:
                raise e

            await asyncio.sleep(1)


async def post(endpoint: str, body: dict = None):
    api_endpoint = "{}/{}".format(API_URL, endpoint)

    for i in range(6):
        try:
            return await asyncio.to_thread(requests.post, api_endpoint, data=body, headers=_get_headers())
        except Exception as e:
            if i == 5:
                raise e

            await asyncio.sleep(1)


async def put(endpoint: str, body: dict = None):
    api_endpoint = "{}/{}".format(API_URL, endpoint)

    for i in range(6):
        try:
            return await asyncio.to_thread(requests.put, api_endpoint, data=body, headers=_get_headers())
        except Exception as e:
            if i == 5:
                raise e

            await asyncio.sleep(1)


async def delete(endpoint: str):
    api_endpoint = "{}/{}".format(API_URL, endpoint)

    for i in range(6):
        try:
            return await asyncio.to_thread(requests.delete, api_endpoint, headers=_get_headers())
        except Exception as e:
            if i == 5:
                raise e

            await asyncio.sleep(1)
