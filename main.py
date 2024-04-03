from flask import Flask
from flask_bootstrap import Bootstrap

def create_app():
    flask_app = Flask(__name__, instance_relative_config=True)
    flask_app.config.from_object("config.DefaultConfig") # can't import DefaultConfig from config.config ?
    Bootstrap(flask_app)

    with flask_app.app_context() as _:
        from routes import flask_routes
        from routes import dash_routes

    return flask_app
    
if __name__ == "__main__":
    flask_app: Flask = create_app()
    flask_port = flask_app.config.get("PORT", 5000)
    flask_app.run(host="0.0.0.0", port=flask_port)
