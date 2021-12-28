import requests
from src.constants import API_URL


def get_cameras() -> list:
    return requests.get("{}/cameras".format(API_URL)).json()
