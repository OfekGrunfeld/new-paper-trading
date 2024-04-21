from comms.encrypt import encrypt
import json
import requests
from typing import Union
from urllib3.exceptions import MaxRetryError

FASTAPI_SERVER_URL = f"https://127.0.0.1:5555"
data = json.dumps({u"type": u"example of json that could be symmetrically encrypted 😀 "})
stored_encrypted_data = encrypt(data.encode("utf-8"))

print(stored_encrypted_data)
def get_testing_response(stored_encrypted_data) -> Union[requests.Response | dict[str, Exception]]:
    try:
        response: requests.Response = requests.post(
            url=f"{FASTAPI_SERVER_URL}/testing",
            params={"encrypted": stored_encrypted_data},
            verify=False,
            timeout=5
        )
        return response
    except MaxRetryError as error:
        print(f"Got too many retries for server: {error}")
        return {"internal_error": error}
    except Exception as error:
        print(f"Got unexpected error: {error}")
        return {"internal_error": error}
    
response = get_testing_response(stored_encrypted_data)

print(response.status_code)

print(json.loads(response.json()))
