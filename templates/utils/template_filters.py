import datetime

from flask import current_app as flask_app

@flask_app.template_filter('format_iso_datetime')
def format_iso_datetime(value: str, format='%d-%m-%Y %H:%M:%S') -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        return ""
    try:
        date_time_obj = datetime.datetime.fromisoformat(value)
        # Return the formatted string
        return date_time_obj.strftime(format)
    except ValueError:
        # Return the original value if parsing fails
        return value  

@flask_app.template_filter('format_total_worths')
def format_total_worths(total_worths: dict) -> float:
    return int(sum(total_worths.values()) * 100) / 100
