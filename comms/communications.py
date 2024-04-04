from typing import Union, Any
import requests
from urllib3.exceptions import MaxRetryError
from os import environ

from utils import logger

SERVER_URL = f"http://127.0.0.1:{environ.get('FASTAPI_PORT')}"

def get_sign_up_response(email: str, username: str, password: str) -> Union[requests.Response | dict[str, Exception]]:
    try:
        response: requests.Response = requests.post(
            url=f"{SERVER_URL}/sign_up",
            params={"email": email, "username": username, "password": password},
            verify=False,
            timeout=5
        )
        return response
    except MaxRetryError as error:
        logger.error(f"Got too many retries for server: {error}")
        return {"internal_error": error}
    except Exception as error:
        logger.error(f"Got unexpected error: {error}")
        return {"internal_error": error}
    

def get_sign_in_response(username: str, password: str):
    try:
        response: requests.Response = requests.post(
            url=f"{SERVER_URL}/sign_in",
            params={"username": username, "password": password},
            verify=False,
            timeout=5
        )
        return response
    except MaxRetryError as error:
        logger.error(f"Got too many retries for server: {error}")
        return {"internal_error": error}
    except Exception as error:
        logger.error(f"Got unexpected error: {error}")
        return {"internal_error": error}
