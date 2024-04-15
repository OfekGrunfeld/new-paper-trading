from os import environ

class DefaultConfig:
    """Flask configuration variables."""

    # General Config
    APP_NAME = environ.get("APP_NAME")
    DEBUG = environ.get("FLASK_DEBUG")
    TESTING = environ.get("FLASK_TESTING")
    SECRET_KEY =  environ.get("SECRET_KEY")
    PORT = environ.get("FLASK_PORT")

    # Static Assets
    STATIC_FOLDER = "static"
    TEMPLATE_FOLDER = "templates"