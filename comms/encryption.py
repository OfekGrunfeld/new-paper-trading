from typing import Union
import os
from base64 import b64encode, b64decode
import json

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from utils.env_variables import SECRET_KEY
from utils.logger_script import logger

backend = default_backend()

def pad_binary_data(binary_data: bytes) -> bytes:
    """
    Pad the binary data with null bytes to ensure the length is a multiple of the block size.

    This is necessary because the AES cipher requires the input data to be a multiple of the block size (16 bytes).

    Args:
        binary_data (bytes): The binary data to be padded.

    Returns:
        bytes: The padded binary data.
    """
    try:
        block_size = 16
        padding_length = block_size - (len(binary_data) % block_size)
        return binary_data + b"\0" * padding_length
    except Exception as error:
        logger.error(f"Error padding data. Error: {error}")

def encrypt(data: Union[str, dict]) -> str:
    """
    Encrypts given data using AES encryption in CBC mode with a dynamically generated initialization vector.

    Args:
        data (Union[str, dict]): The data to be encrypted. If the data is a string, it's encoded to bytes. 
                                 If it is a dictionary, it is converted to a JSON string and then to bytes.

    Returns:
        str: A string composed of the base64-encoded initialization vector, the length of the original 
             binary data, and the encrypted data. These components are concatenated with a dollar sign ('$')
             as the delimiter, allowing for easy parsing upon decryption.

    Notes:
        The encryption key and IV are derived from predefined environmental variables and are not hard-coded 
        within this function. The backend for the cryptographic operations is set to the default cryptographic
        backend provided by the 'cryptography' package.
    """
    if isinstance(data, str):
        binary_data = data.encode("utf-8")
    if isinstance(data, dict):
        binary_data = json.dumps(data).encode("utf-8")
    padded_data = pad_binary_data(binary_data)
    iv = os.urandom(16)  # The initialization vector (IV) must be unpredictable

    cipher = Cipher(
        algorithms.AES(b64decode(SECRET_KEY)), 
        modes.CBC(iv), 
        backend=backend
    )
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    # Serialize the encrypted data, IV, and original data length for storage
    return f"{b64encode(iv).decode()}${len(binary_data)}${b64encode(encrypted_data).decode()}"