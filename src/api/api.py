from requests import Session, Response
from src.constants import API_URL
import time
import logging


SESSION = Session()


def set_headers(headers: dict):
    SESSION.headers = headers


def _execute_and_retry_on_failure(callback, error_message: str) -> Response:
    for i in range(6):
        try:
            return callback()
        except Exception as e:
            logging.info(f"{error_message}: {str(e)}")
            if i == 5:
                raise e

            time.sleep(1)


def get(endpoint: str) -> Response:
    api_endpoint = "{}/{}".format(API_URL, endpoint)

    def do_get() -> Response:
        return SESSION.get(api_endpoint)

    return _execute_and_retry_on_failure(do_get, f"Error getting @ {endpoint}")


def post(endpoint: str, body: dict = None) -> Response:
    api_endpoint = "{}/{}".format(API_URL, endpoint)

    def do_post() -> Response:
        return SESSION.post(api_endpoint, data=body)

    return _execute_and_retry_on_failure(do_post, f"Error posting @ {endpoint}")


def put(endpoint: str, body: dict = None) -> Response:
    api_endpoint = "{}/{}".format(API_URL, endpoint)

    def do_put() -> Response:
        return SESSION.put(api_endpoint, data=body)

    return _execute_and_retry_on_failure(do_put, f"Error putting @ {endpoint}")


def delete(endpoint: str) -> Response:
    api_endpoint = "{}/{}".format(API_URL, endpoint)

    def do_delete() -> Response:
        return SESSION.delete(api_endpoint)

    return _execute_and_retry_on_failure(do_delete, f"Error deleting @ {endpoint}")
