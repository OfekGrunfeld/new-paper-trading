from requests import Response

from flask import current_app as flask_app, jsonify, render_template, abort
from werkzeug.utils import import_string


@flask_app.route('/routes', methods=['GET'])
def routes_info():
    """
    Print all defined routes and their endpoint docstrings only when in debug mode.
    """
    if not flask_app.config.get('DEBUG', False):
        # Abort with a 403 Forbidden if not in debug mode
        abort(403, description="Access denied: Route information is available only in debug mode.")

    routes = []
    for rule in flask_app.url_map.iter_rules():
        if rule.endpoint != 'static':
            try:
                view_func = flask_app.view_functions[rule.endpoint]
                if hasattr(view_func, 'import_name'):
                    import_name = view_func.import_name
                    obj = import_string(import_name)
                    doc = obj.__doc__
                else:
                    doc = view_func.__doc__

                methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
                routes.append((rule.rule, methods, doc.strip() if doc else "No documentation provided."))
            except Exception as exc:
                flask_app.logger.error("Error processing rule: %s" % rule.rule, exc_info=True)
                routes.append((rule.rule, 'ERROR', 'Invalid route definition!'))

    return render_template('misc/routes.html', routes=routes)