from wtforms.validators import Length, Email, DataRequired, Optional

class DefaultFormValidators:
    barebones_email = [Email(),Length(min=6, max=64)]
    email = [DataRequired()].extend(barebones_email)
    new_email = [Optional()].extend(barebones_email)
    
    barebones_username =  [Length(min=2, max=25)]
    username = [DataRequired()].extend(barebones_username)
    new_username = [Optional()].extend(barebones_username)

    barebones_password = [Length(min=5, max=64)]
    password = [DataRequired()].extend(barebones_password)
    new_password = [Optional()].extend(barebones_password)

    symbol_pick = [DataRequired(), Length(min=2, max=64)]

    number_error_message = "Please enter a valid number"
