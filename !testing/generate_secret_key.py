# IMPORT
from flask import Flask
from flask_bcrypt import Bcrypt
import secrets

def get_secret_key(flask_app: Flask) -> str:
    # Create hex Key
    secret_key = secrets.token_hex(16) 
    # Init Bcrypt
    bcrypt = Bcrypt(flask_app) 
    #hash the HEX key with Bcrypt
    secret_key_hash: bytes = bcrypt.generate_password_hash(secret_key) 
    
    return secret_key_hash