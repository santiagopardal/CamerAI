from requests import Session
from src.constants import API_URL
import asyncio
import logging


SESSION = Session()


def set_headers(headers: dict):
    SESSION.headers = headers


async def get(endpoint: str):
    api_endpoint = "{}/{}".format(API_URL, endpoint)

    for i in range(6):
        try:
            return await asyncio.to_thread(SESSION.get, api_endpoint)
        except Exception as e:
            logging.info(f"Error getting @ {endpoint}: {str(e)}")
            if i == 5:
                raise e

            await asyncio.sleep(1)


async def post(endpoint: str, body: dict = None):
    api_endpoint = "{}/{}".format(API_URL, endpoint)

    for i in range(6):
        try:
            return await asyncio.to_thread(SESSION.post, api_endpoint, data=body)
        except Exception as e:
            logging.info(f"Error posting @ {endpoint}: {str(e)}")
            if i == 5:
                raise e

            await asyncio.sleep(1)


async def put(endpoint: str, body: dict = None):
    api_endpoint = "{}/{}".format(API_URL, endpoint)

    for i in range(6):
        try:
            return await asyncio.to_thread(SESSION.put, api_endpoint, data=body)
        except Exception as e:
            logging.info(f"Error putting @ {endpoint}: {str(e)}")
            if i == 5:
                raise e

            await asyncio.sleep(1)


async def delete(endpoint: str):
    api_endpoint = "{}/{}".format(API_URL, endpoint)

    for i in range(6):
        try:
            return await asyncio.to_thread(SESSION.delete, api_endpoint)
        except Exception as e:
            logging.info(f"Error deleting @ {endpoint}: {str(e)}")
            if i == 5:
                raise e

            await asyncio.sleep(1)
