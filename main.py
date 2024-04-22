from flask import Flask
from flask_bootstrap import Bootstrap
from utils import ItsdangerousSessionInterface

def create_app():
    flask_app = Flask(__name__, instance_relative_config=True)
    flask_app.config.from_object("utils.DefaultConfig")
    Bootstrap(flask_app)
    flask_app.session_interface = ItsdangerousSessionInterface() 

    with flask_app.app_context() as _:
        # Dash routes
        from routes import dash_routes

        # Flask Routes
        from routes import flask_routes
        from routes import flask_routes_helper
        from routes import flask_users

        # Jinja templates
        from templates.utils import template_filters

    return flask_app

flask_app: Flask = create_app()
flask_port = flask_app.config.get("PORT", 5000)
    
def run_flask():
    flask_app.run(host="0.0.0.0", port=flask_port)

if __name__ == "__main__":
    run_flask()
    
    
