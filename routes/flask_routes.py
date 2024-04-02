from pathlib import Path
import re

from flask import current_app as flask_app
from flask import render_template
import markdown
import markdown.extensions.fenced_code
from markupsafe import Markup
from pygments.formatters.html import HtmlFormatter

from utils.render_readme import get_rendered_readme


@flask_app.route("/")
def index() -> str:
    return get_rendered_readme()
    


@flask_app.route("/tradingview", methods=["GET", "POST"])
def tradingview_page() -> str:
    return render_template(
        "tradingview.html"
        )
