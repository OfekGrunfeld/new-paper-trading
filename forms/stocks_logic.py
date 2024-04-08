from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, IntegerField, BooleanField, RadioField
from wtforms.validators import DataRequired, Optional, NumberRange

from forms.defaults import DefaultFormValidators

class SymbolPickForm(FlaskForm):
    symbol = StringField("Symbol", validators=DefaultFormValidators.symbol_pick)

class TradeForm(FlaskForm):
    order_type = SelectField("Order Type", choices=[('market', 'Market'), ('limit', 'Limit'), ('stop', 'Stop'), ('stop_limit', 'Stop-Limit')], validators=[DataRequired()])
    side = RadioField("Side", choices=[('buy', 'Buy'), ('sell', 'Sell')], default="buy")
    quantity = IntegerField("Quantity", validators=[NumberRange(min=0, message='bla1')])
    limit_price = DecimalField("Limit Price", validators=[NumberRange(min=0, message='bla2')])
    stop_price = DecimalField("Stop Price", validators=[NumberRange(min=0, message='bla3')])
    time_in_force = SelectField("Time in Force", choices=[('day', 'Day'), ('gtc', 'GTC')], validators=[DataRequired()], default='day')
    stop_loss_check = BooleanField("Stop-Loss Order")
    take_profit_check = BooleanField("Take-Profit Order")

def get_locked_trade_form() -> TradeForm:
    """"
    Get a trade form with every field locked
    """
    tf = TradeForm()
    for field in tf:
        field.render_kw = {'disabled': 'disabled'}
    
    return tf