from flask import current_app as flask_app

from flask_dash.graphs import DashPieChart

# The following components are actually routes in the website and used as iFrames
shares_graph = DashPieChart(flask_app, r"/my/portfolio/graphs/shares/")
worths_graph = DashPieChart(flask_app, r"/my/portfolio/graphs/worths/")