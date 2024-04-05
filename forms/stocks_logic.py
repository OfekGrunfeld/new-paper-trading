from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField

from forms.defaults import DefaultFormValidators

class SymbolPickForm(FlaskForm):
    symbol = StringField("Symbol", validators=DefaultFormValidators.symbol_pick)