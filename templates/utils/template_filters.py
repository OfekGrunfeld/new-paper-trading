import datetime

from flask import current_app as flask_app

@flask_app.template_filter('format_iso_datetime')
def format_iso_datetime(value: str, format='%d-%m-%Y %H:%M:%S'):
    if value is None:
        return ""
    if not isinstance(value, str):
        print(f"what {type(value)}")
    try:
        date_time_obj = datetime.datetime.fromisoformat(value)
        # Return the formatted string
        return date_time_obj.strftime(format)
    except ValueError:
        # Return the original value if parsing fails
        return value  
        
