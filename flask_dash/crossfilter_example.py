import numpy as np
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from flask import Flask

from flask_dash.flask_dash_integrator import FlaskDash

df: pd.DataFrame = pd.read_csv("data/indicators.csv")  # noqa: PD901
available_indicators: np.ndarray = df["Indicator Name"].unique()

def create_page_layout() -> dbc.Container:
    """
    Create the layout for this page
    """
    page_layout = dbc.Container(
        [
            html.H1("Crossfilter example"),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dcc.Dropdown(
                                        id="crossfilter-xaxis-column",
                                        options=[
                                            {"label": i, "value": i}
                                            for i in available_indicators
                                        ],
                                        value="Fertility rate, total (births per woman)",
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.RadioItems(
                                                id="crossfilter-xaxis-type",
                                                inline=True,
                                                options=[
                                                    {"label": i, "value": i}
                                                    for i in ["Linear", "Log"]
                                                ],
                                                value="Linear",
                                                labelStyle={"display": "inline-block"},
                                            ),
                                        ],
                                        className="p-2",
                                    ),
                                ]
                            ),
                            dbc.Card(
                                [
                                    dcc.Graph(
                                        id="crossfilter-indicator-scatter",
                                        hoverData={"points": [{"customdata": "Japan"}]},
                                    )
                                ],
                                # style={
                                #     "width": "49%",
                                #     "display":
                                #     "inline-block",
                                #     "padding":
                                #     "0 20"
                                # },
                            ),
                            dbc.Card(
                                dcc.Slider(
                                    id="crossfilter-year--slider",
                                    min=df["Year"].min(),
                                    max=df["Year"].max(),
                                    value=df["Year"].max(),
                                    step=None,
                                    marks={
                                        str(year): str(year) for year in df["Year"].unique()
                                    },
                                ),
                                className="pt-2"
                                # style={"width": "49%", "padding": "0px 20px 20px 20px"},
                            ),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dcc.Dropdown(
                                        id="crossfilter-yaxis-column",
                                        options=[
                                            {"label": i, "value": i}
                                            for i in available_indicators
                                        ],
                                        value="Life expectancy at birth, total (years)",
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.RadioItems(
                                                id="crossfilter-yaxis-type",
                                                inline=True,
                                                options=[
                                                    {"label": i, "value": i}
                                                    for i in ["Linear", "Log"]
                                                ],
                                                value="Linear",
                                                labelStyle={"display": "inline-block"},
                                            ),
                                        ],
                                        className="p-2",
                                    ),
                                ]
                            ),
                            dbc.Card(
                                [
                                    dcc.Graph(id="x-time-series"),
                                    dcc.Graph(id="y-time-series"),
                                ],
                                # style={"display": "inline-block", "width": "49%"},
                            ),
                        ],
                        md=6,
                    ),
                ],
            ),
        ],
        fluid=True,
    )

    return page_layout

page_layout = create_page_layout()

def update_graph(
    xaxis_column_name, yaxis_column_name, xaxis_type, yaxis_type, year_value
):
    dff = df[df["Year"] == year_value]

    return {
        "data": [
            go.Scatter(
                x=dff[dff["Indicator Name"] == xaxis_column_name]["Value"],
                y=dff[dff["Indicator Name"] == yaxis_column_name]["Value"],
                text=dff[dff["Indicator Name"] == yaxis_column_name]["Country Name"],
                customdata=dff[dff["Indicator Name"] == yaxis_column_name][
                    "Country Name"
                ],
                mode="markers",
                marker={
                    "size": 15,
                    "opacity": 0.5,
                    "line": {"width": 0.5, "color": "white"},
                },
            )
        ],
        "layout": go.Layout(
            xaxis={
                "title": xaxis_column_name,
                "type": "linear" if xaxis_type == "Linear" else "log",
            },
            yaxis={
                "title": yaxis_column_name,
                "type": "linear" if yaxis_type == "Linear" else "log",
            },
            # margin={"l": 40, "b": 30, "t": 10, "r": 0},
            margin={"l": 80, "b": 60, "t": 20, "r": 20},
            height=450,
            hovermode="closest",
        ),
    }

def create_time_series(dff, axis_type, title):
    return {
        "data": [go.Scatter(x=dff["Year"], y=dff["Value"], mode="lines+markers")],
        "layout": {
            "height": 225,
            # "margin": {"l": 20, "b": 30, "r": 10, "t": 10},
            "margin": {"l": 40, "b": 60, "r": 20, "t": 20},
            "annotations": [
                {
                    "x": 0,
                    "y": 0.85,
                    "xanchor": "left",
                    "yanchor": "bottom",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "align": "left",
                    "bgcolor": "rgba(255, 255, 255, 0.5)",
                    "text": title,
                }
            ],
            "yaxis": {"type": "linear" if axis_type == "Linear" else "log"},
            "xaxis": {"showgrid": False},
        },
    }

def update_y_timeseries(hoverData, xaxis_column_name, axis_type):
    country_name = hoverData["points"][0]["customdata"]
    dff = df[df["Country Name"] == country_name]
    dff = dff[dff["Indicator Name"] == xaxis_column_name]
    title = f"<b>{country_name}</b><br>{xaxis_column_name}"
    return create_time_series(dff, axis_type, title)

def update_x_timeseries(hoverData, yaxis_column_name, axis_type):
    dff = df[df["Country Name"] == hoverData["points"][0]["customdata"]]
    dff = dff[dff["Indicator Name"] == yaxis_column_name]
    return create_time_series(dff, axis_type, yaxis_column_name)

def init_callbacks(flask_dash_app: FlaskDash):
    flask_dash_app.callback(
        Output("crossfilter-indicator-scatter", "figure"),
        [
            Input("crossfilter-xaxis-column", "value"),
            Input("crossfilter-yaxis-column", "value"),
            Input("crossfilter-xaxis-type", "value"),
            Input("crossfilter-yaxis-type", "value"),
            Input("crossfilter-year--slider", "value"),
        ],
    )(update_graph)

    flask_dash_app.callback(
        Output("x-time-series", "figure"),
        [
            Input("crossfilter-indicator-scatter", "hoverData"),
            Input("crossfilter-xaxis-column", "value"),
            Input("crossfilter-xaxis-type", "value"),
        ],
    )(update_y_timeseries)

    flask_dash_app.callback(
        Output("y-time-series", "figure"),
        [
            Input("crossfilter-indicator-scatter", "hoverData"),
            Input("crossfilter-yaxis-column", "value"),
            Input("crossfilter-yaxis-type", "value"),
        ],
    )(update_x_timeseries)

    return flask_dash_app

def init_flask_dash_app(server: Flask):
    """Create a Plotly Dash dashboard."""
    flask_dash_app = FlaskDash(
        server=server,
        routes_pathname_prefix="/crossfilter-example/",
    )

    # create dash layout
    flask_dash_app.layout = page_layout

    # initialize callbacks
    init_callbacks(flask_dash_app)

    return flask_dash_app.server


if __name__ == "__main__":
    flask_dash_app = FlaskDash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    init_callbacks(flask_dash_app)
    flask_dash_app.run_server(debug=True, port=8080)
