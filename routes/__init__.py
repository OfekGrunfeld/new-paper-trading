__all__: list[str] = ["dash_routes", "flask_routes"]
from . import *
from .flask_user_routes import format_iso_datetime
from jinja2 import Environment

# Assuming you're setting up your Jinja environment
env = Environment()

# Add your custom filter
env.filters['format_iso_datetime'] = format_iso_datetime