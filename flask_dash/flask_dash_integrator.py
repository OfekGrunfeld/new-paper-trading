from typing import override

from dash import Dash
from flask import render_template
from markupsafe import Markup

class FlaskDash(Dash):
    @override
    def interpolate_index(
        self,
        metas="",
        title="", 
        css="",
        config="",
        scripts="",
        app_entry="",
        favicon="",
        renderer="",
    ) -> str:
        """
        Override the default interpolate_index function in order to provide
        support for flask
        """
        # markupsafe.Markup is used to prevent Jinja from
        # escaping the Dash-rendered markup
        return render_template(
            "misc/dash.html",
            metas=Markup(metas),
            css=Markup(css),
            # config is mapped to dash_config
            # to avoid shadowing the global Flask config
            # in the Jinja environment
            dash_config=Markup(config),
            scripts=Markup(scripts),
            app_entry=Markup(app_entry),
            renderer=Markup(renderer),
        )
