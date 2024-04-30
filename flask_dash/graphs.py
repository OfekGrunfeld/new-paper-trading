from dash import dcc
import dash_bootstrap_components as dbc
from plotly import express as px

from .flask_dash_integrator import FlaskDash

class GraphCreator:
    """
    Used for organizing graph/chart creation functions.
    """
    @staticmethod
    def create_chart_pie(data_to_display: dict = None):
        """
        Generates a pie chart using provided data.

        This method uses Plotly Express to create a pie chart visualization which is then
        placed into a Dash Bootstrap Container. If no data is provided, it uses a default
        set of values.

        Parameters:
            data (dict, optional): A dictionary where keys represent the categories and
                                values represent the numeric values for those categories.

        Returns:
            dbc.Container: A Dash Bootstrap Container component that includes the generated pie chart.
        """

        if data_to_display is None:
            data_to_display = {"This": 1, "is": 2, "a": 3, "default": 4, "value": 5}
            
        # Create a pie chart using Plotly Express
        fig = px.pie(
            names=list(data_to_display.keys()), 
            values=list(data_to_display.values()), 
        )

        page_layout = dbc.Container(
            [
                dcc.Graph(figure=fig) 
            ],
            fluid=True,
        )
        return page_layout

class DashPieChart:
    def __init__(self, server, route: str, data: dict = None):
        self.flask_dash_app = FlaskDash(
            server=server,
            routes_pathname_prefix=route,
        )
        self.change_page_layout(data)

    def change_page_layout(self, data_for_graph: dict):
        self.flask_dash_app.layout = GraphCreator.create_chart_pie(data_for_graph)