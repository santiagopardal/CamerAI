import time
import requests
from src.constants import API_URL


NODE = None


def _get_headers():
    global NODE
    if NODE and NODE.id:
        return {"node_id": str(NODE.id)}

    return None


def get(endpoint: str):
    api_endpoint = "{}/{}".format(API_URL, endpoint)

    for i in range(6):
        try:
            return requests.get(api_endpoint, headers=_get_headers())
        except Exception as e:
            if i == 5:
                raise e

            time.sleep(2 ** (i + 1))


def post(endpoint: str, body: dict = None):
    api_endpoint = "{}/{}".format(API_URL, endpoint)

    for i in range(6):
        try:
            return requests.post(api_endpoint, data=body, headers=_get_headers())
        except Exception as e:
            if i == 5:
                raise e

            time.sleep(2 ** (i + 1))


def put(endpoint: str, body: dict = None):
    api_endpoint = "{}/{}".format(API_URL, endpoint)

    for i in range(6):
        try:
            return requests.put(api_endpoint, data=body, headers=_get_headers())
        except Exception as e:
            if i == 5:
                raise e

            time.sleep(2 ** (i + 1))


def delete(endpoint: str):
    api_endpoint = "{}/{}".format(API_URL, endpoint)

    for i in range(6):
        try:
            return requests.delete(api_endpoint, headers=_get_headers())
        except Exception as e:
            if i == 5:
                raise e

            time.sleep(2 ** (i + 1))
