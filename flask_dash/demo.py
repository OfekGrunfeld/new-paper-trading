from dash import html
import dash_bootstrap_components as dbc
from flask import Flask

from .flask_dash_integrator import FlaskDash

def create_page_layout():
    """
    Create the layout for this page
    """
    page_layout = dbc.Container( 
        [
            html.H1(children="Hello Dash"),
        ],
        fluid=True,
    )
    return page_layout

page_layout = create_page_layout()


def init_flask_dash_app(server: Flask) -> Flask :
    flask_dash_app = FlaskDash(
        server=server,
        routes_pathname_prefix="/demo/",
    )
    flask_dash_app.layout = page_layout
    return flask_dash_app.server

if __name__ == "__main__":
    flask_dash_app = FlaskDash(__name__)
    flask_dash_app.run_server(debug=True)
