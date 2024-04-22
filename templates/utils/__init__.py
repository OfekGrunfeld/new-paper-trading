from .template_filters import format_iso_datetime

from jinja2 import Environment

env = Environment()
env.filters['format_iso_datetime'] = format_iso_datetime