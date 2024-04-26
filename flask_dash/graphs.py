from dash import dcc
import dash_bootstrap_components as dbc
from plotly import express as px

from .flask_dash_integrator import FlaskDash


class GraphCreator:
    @staticmethod
    def create_chart_pie(data: dict = None):
        """
        Create the layout for this page, including a pie chart based on a dictionary.
        
        Parameters:
            data (dict): A dictionary
        """
        if data is None:
            data = {"This": 1, "is": 2, "a": 3, "default": 4, "value": 5}
            
        # Create a pie chart using Plotly Express
        fig = px.pie(
            names=list(data.keys()), 
            values=list(data.values()), 
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