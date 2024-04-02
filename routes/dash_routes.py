from flask import Flask
from flask import current_app as flask_app
from flask import render_template

from flask_dash import crossfilter_example, demo, iris_kmeans

app: Flask = demo.init_flask_dash_app(flask_app)
app: Flask = iris_kmeans.init_flask_dash_app(flask_app)
app: Flask = crossfilter_example.init_flask_dash_app(flask_app)
