from os import environ

SECRET_KEY =  environ.get("SECRET_KEY")
FASTAPI_IP = environ.get("FASTAPI_IP")
FASTAPI_PORT = environ.get('FASTAPI_PORT')
PORT = environ.get("FLASK_PORT")