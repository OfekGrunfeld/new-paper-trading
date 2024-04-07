from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Optional, NumberRange

from forms.defaults import DefaultFormValidators

class SymbolPickForm(FlaskForm):
    symbol = StringField("Symbol", validators=DefaultFormValidators.symbol_pick)

class TradeForm(FlaskForm):
    order_type = SelectField("Order Type", choices=[('market', 'Market'), ('limit', 'Limit'), ('stop', 'Stop'), ('stop_limit', 'Stop-Limit')], validators=[DataRequired()])
    quantity = IntegerField("Quantity", validators=[NumberRange(min=0, message='bla1')])
    limit_price = DecimalField("Limit Price", validators=[NumberRange(min=0, message='bla2')])
    stop_price = DecimalField("Stop Price", validators=[NumberRange(min=0, message='bla3')])
    time_in_force = SelectField("Time in Force", choices=[('day', 'Day'), ('gtc', 'GTC')], validators=[DataRequired()], default='day')
    stop_loss_check = BooleanField("Stop-Loss Order")
    take_profit_check = BooleanField("Take-Profit Order")