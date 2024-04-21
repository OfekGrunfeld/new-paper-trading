from wtforms.validators import Length, Email, DataRequired

class DefaultFormValidators:
    email = [DataRequired(), Email(),Length(min=6, max=64)]
    username = [DataRequired(), Length(min=2, max=25)]
    password = [DataRequired(), Length(min=5, max=64)]

    symbol_pick = [DataRequired(), Length(min=2, max=64)]
