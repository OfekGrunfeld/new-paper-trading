from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField

from forms.defaults import DefaultFormValidators

class SignUpForm(FlaskForm):
    email = StringField("Email", validators=DefaultFormValidators.email)
    username = StringField("Username", validators=DefaultFormValidators.username)
    password = PasswordField("Password", validators=DefaultFormValidators.password)
    repeat_password = PasswordField(label="repated_password", validators=DefaultFormValidators.password)


class SignInForm(FlaskForm):
    username = StringField("Username", validators=DefaultFormValidators.username)
    password = PasswordField("Password", validators=DefaultFormValidators.password)


