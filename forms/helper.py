from wtforms.validators import Length, Email, DataRequired, Optional

class DefaultFormValidators:
    email = [DataRequired(), Email(),Length(min=6, max=64)]
    username = [DataRequired(), Length(min=2, max=25)]
    password = [DataRequired(), Length(min=5, max=64)]

    new_email = [Optional(), Email(),Length(min=6, max=64)]
    new_username = [Optional(), Length(min=2, max=25)]
    new_password = [Optional(), Length(min=5, max=64)]

    symbol_pick = [DataRequired(), Length(min=2, max=64)]
