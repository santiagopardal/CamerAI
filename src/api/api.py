import time
import requests
from src.constants import API_URL


async def get(endpoint: str):
    api_endpoint = "{}/{}".format(API_URL, endpoint)

    for i in range(6):
        try:
            return requests.get(api_endpoint)
        except Exception as e:
            if i == 5:
                raise e

            time.sleep(2 ** (i + 1))


async def post(endpoint: str):
    api_endpoint = "{}/{}".format(API_URL, endpoint)

    for i in range(6):
        try:
            return requests.post(api_endpoint)
        except Exception as e:
            if i == 5:
                raise e

            time.sleep(2 ** (i + 1))


async def put(endpoint: str, body: dict):
    api_endpoint = "{}/{}".format(API_URL, endpoint)

    for i in range(6):
        try:
            return requests.put(api_endpoint, data=body)
        except Exception as e:
            print(e)
            if i == 5:
                raise e

            time.sleep(2 ** (i + 1))


async def delete(endpoint: str):
    api_endpoint = "{}/{}".format(API_URL, endpoint)

    for i in range(6):
        try:
            return requests.delete(api_endpoint)
        except Exception as e:
            if i == 5:
                raise e

            time.sleep(2 ** (i + 1))
