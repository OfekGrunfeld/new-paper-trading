import os
from base64 import b64encode, b64decode
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import json
from utils import DefaultConfig
import traceback

from utils import logger

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
        logger.critical(traceback.format_exc())


def encrypt(data) -> str:
    """
    Encrypt the binary data using AES-CBC.

    Args:
        binary_data (bytes): The binary data to be encrypted.

    Returns:
        str: The encrypted data, serialized as a string.
    """
    if isinstance(data, str):
        binary_data = data.encode("utf-8")
    if isinstance(data, dict):
        binary_data = json.dumps(data).encode("utf-8")
    logger.debug(f"Binary data: {binary_data}")
    padded_data = pad_binary_data(binary_data)
    iv = os.urandom(16)  # The initialization vector (IV) must be unpredictable

    cipher = Cipher(algorithms.AES(b64decode(DefaultConfig.SECRET_KEY)), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    # Serialize the encrypted data, IV, and original data length for storage
    return f"{b64encode(iv).decode()}${len(binary_data)}${b64encode(encrypted_data).decode()}"
