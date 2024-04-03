from enum import Enum

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Length, Email, DataRequired

class DefaultFormValidators:
    email = [DataRequired(), Email(),Length(min=6, max=64)]
    username = [DataRequired(), Length(min=2, max=25)]
    password = [DataRequired(), Length(min=5, max=64)]

class SignUpForm(FlaskForm):
    email = StringField('Email', validators=DefaultFormValidators.email)
    username = StringField('Username', validators=DefaultFormValidators.username)
    password = PasswordField('Password', validators=DefaultFormValidators.password)
    repeat_password = PasswordField(label="repated_password", validators=DefaultFormValidators.password)


class LoginForm(FlaskForm):
    username = StringField('Username', validators=DefaultFormValidators.username)
    password = PasswordField('Password', validators=DefaultFormValidators.password)


