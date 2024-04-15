from os import environ

class EnvironmentVariables:
    SECRET_KEY =  environ.get("SECRET_KEY")
    FASTAPI_PORT = environ.get('FASTAPI_PORT')
    PORT = environ.get("FLASK_PORT")