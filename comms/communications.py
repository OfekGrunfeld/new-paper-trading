from enum import Enum
from typing import Union, Any
import requests
from urllib3.exceptions import MaxRetryError

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
    get_database = "get_user/database"

def get_response(endpoint: str, method: str, data_to_send: dict = {}) -> dict:
    """
    Sends a request to a specified endpoint on the FastAPI server using an HTTP method and data provided,
    handling session-specific parameters, encryption of data, and response management.

    Args:
        endpoint (str): The endpoint of the FastAPI server to which the request is sent.
        method (str): The HTTP method to be used for the request. Acceptable methods are 'get', 'post', 'put', and 'delete'.
        data_to_send (dict, optional): A dictionary of the data to send to the endpoint. Default is an empty dictionary.

    Returns:
        dict: A dictionary containing the JSON response from the server if the request is successful, or
            an error dictionary if an exception occurs.

    Raises:
        ValueError: If an unsupported HTTP method is specified.
        HTTPException: If the request fails for reasons such as network errors or server-side issues.

    Notes:
        - The function automatically handles encryption of the data sent based on predefined requirements.
        - It also manages specific routing and parameter inclusion for certain types of requests identified by their endpoints.
    """
    try:
        
        routes_that_need_uuid = [FastAPIRoutes.get_portfolio.value, FastAPIRoutes.submit_order.value, FastAPIRoutes.update_user.value, FastAPIRoutes.get_database.value]
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
            logger.debug(f"Got response from fastAPI server: {response.status_code}")
            response_json: dict = response.json()
            logger.debug(f"Data: {response_json}")
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