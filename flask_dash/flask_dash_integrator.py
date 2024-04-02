import dash
from flask import render_template
from markupsafe import Markup

class FlaskDash(dash.Dash):
    def interpolate_index(
        self,
        metas="",
        title="",  # noqa: ARG002
        css="",
        config="",
        scripts="",
        app_entry="",
        favicon="",  # noqa: ARG002
        renderer="",
    ) -> str:
        """
        Override the default interpolate_index function in order to provide
        support for flask
        """
        # markupsafe.Markup is used to prevent Jinja from
        # escaping the Dash-rendered markup
        return render_template(
            "dash.html",
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
