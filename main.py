from flask import Flask, render_template, redirect

flask_app = Flask(__name__, instance_relative_config=True)
flask_app.config.from_object("config.DefaultConfig")

with flask_app.app_context() as _:
    from routes import flask_routes
    from routes import dash_routes
    

if __name__ == "__main__":
    # Only for debugging while developing
    flask_app.run(host="0.0.0.0", debug=True, port=8080)
