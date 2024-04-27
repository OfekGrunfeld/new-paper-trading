from enum import Enum
from typing import Union, Any
import requests
from urllib3.exceptions import MaxRetryError
import traceback

from flask import session

from utils import logger
from utils.env_variables import FASTAPI_IP, FASTAPI_PORT
from comms.encryption import encrypt

FASTAPI_SERVER_URL = f"{FASTAPI_IP}:{FASTAPI_PORT}"

class FastAPIRoutes(Enum):
    sign_up = "sign_up"
    sign_in = "sign_in"
    update_user = "update" # add attribute to update at the end
    submit_order = "submit_order"
    get_portfolio ="get_user/summary"

def get_response(endpoint: str, method: str, data_to_send: dict = {}) -> dict:
    try:
        routes_that_need_uuid = [FastAPIRoutes.get_portfolio.value, FastAPIRoutes.submit_order.value, FastAPIRoutes.update_user.value]
        # Add uuid for special endpoints
        if any(endpoint.startswith(route) for route in routes_that_need_uuid):
            data_to_send["uuid"] = session["uuid"]
        if endpoint.startswith(FastAPIRoutes.update_user.value):
            data_to_send["password"] = session["password"]

        # Encrypt each value in the data_to_send dictionary before sending
        encrypted_data = {key: encrypt(value) for key, value in data_to_send.items()}

        # Get the correct requests method based on the string
        method_func: Union[requests.get, requests.post, requests.delete, requests.put] = getattr(requests, method.lower(), None)

        if not method_func:
            raise ValueError(f"Unsupported HTTP method: {method}")

        # Prepare the URL
        url = f"{FASTAPI_SERVER_URL}/{endpoint}"

        # Depending on the method, we may need to send data differently
        if method.lower() in ['get', 'delete', 'post', 'put']:
            response = method_func(url, params=encrypted_data, verify=False, timeout=5)
        
        try:
            logger.warning(f"Response text: {response.text}")
            response_json: dict = response.json()
            return response_json 
        except Exception as error:
            logger.error(f"Failed to get json of response")
            return None
    except MaxRetryError as error:
        logger.error(f"Got too many retries for server: {error}")
        return {"internal_error": error}
    except Exception as error:
        logger.error(f"Got unexpected error: {error}")
        return {"internal_error": error}