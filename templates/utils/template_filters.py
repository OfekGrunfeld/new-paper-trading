import datetime

from flask import current_app as flask_app

@flask_app.template_filter('format_iso_datetime')
def format_iso_datetime(value, format='%d-%m-%Y %H:%M:%S'):
    if value is None:
        return ""
    try:
        date_time_obj = datetime.datetime.fromisoformat(value)
        # Return the formatted string
        return date_time_obj.strftime(format)
    except ValueError:
        # Return the original value if parsing fails
        return value  
        
