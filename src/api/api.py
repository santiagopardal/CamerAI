import tenacity
from requests import Session, Response
from src.constants import API_URL


SESSION = Session()


def set_headers(headers: dict):
    SESSION.headers = headers


@tenacity.retry(
    wait=tenacity.wait_exponential(
        multiplier=1,
        min=4,
        max=60,
        exp_base=2
    ),
    stop=tenacity.stop_after_attempt(6)
)
def get(endpoint: str) -> Response:
    api_endpoint = "{}/{}".format(API_URL, endpoint)
    return SESSION.get(api_endpoint)


@tenacity.retry(
    wait=tenacity.wait_exponential(
        multiplier=1,
        min=4,
        max=60,
        exp_base=2
    ),
    stop=tenacity.stop_after_attempt(6)
)
def post(endpoint: str, body: dict = None) -> Response:
    api_endpoint = "{}/{}".format(API_URL, endpoint)
    return SESSION.post(api_endpoint, data=body)


@tenacity.retry(
    wait=tenacity.wait_exponential(
        multiplier=1,
        min=4,
        max=60,
        exp_base=2
    ),
    stop=tenacity.stop_after_attempt(6)
)
def delete(endpoint: str) -> Response:
    api_endpoint = "{}/{}".format(API_URL, endpoint)
    return SESSION.delete(api_endpoint)
