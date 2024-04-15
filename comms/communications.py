from flask import session

from typing import Union, Any
import requests
from urllib3.exceptions import MaxRetryError

from utils import logger
from utils.env_variables import EnvironmentVariables
from comms.symmetric_crypto import encrypt

FASTAPI_SERVER_URL = f"https://127.0.0.1:{EnvironmentVariables.FASTAPI_PORT}"


def get_sign_up_response(email: str, username: str, password: str) -> Union[requests.Response | dict[str, Exception]]:
    try:
        response: requests.Response = requests.post(
            url=f"{FASTAPI_SERVER_URL}/sign_up",
            json=encrypt({"email": email, "username": username, "password": password}),
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
            url=f"{FASTAPI_SERVER_URL}/sign_in",
            json=encrypt({"username": username, "password": password}),
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
    
def submit_order(order: dict):
    try:
        response: requests.Response = requests.post(
            url=f"{FASTAPI_SERVER_URL}/submit_order",
            json=encrypt({"id": session["user_id"], "order": order}),
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
