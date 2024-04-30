from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, EmailField
from wtforms.validators import DataRequired, Optional

from forms.helper import DefaultFormValidators

class SignUpForm(FlaskForm):
    email = EmailField("Email", validators=DefaultFormValidators.email)
    username = StringField("Username", validators=DefaultFormValidators.username)
    password = PasswordField("Password", validators=DefaultFormValidators.password)
    repeat_password = PasswordField(label="Repeat Password", validators=DefaultFormValidators.password)

class SignInForm(FlaskForm):
    username = StringField("Username", validators=DefaultFormValidators.username)
    password = PasswordField("Password", validators=DefaultFormValidators.password)

class UpdateUserForm(FlaskForm):
    password = PasswordField("Password", validators=DefaultFormValidators.password)
    attribute_to_update = SelectField(
        "Update Field", 
        choices=[('email', 'Email'), ('username', 'Username'), ('password', 'Password')], 
        validators=[DataRequired()],
        option_widget="Select"
    )
    new_email = EmailField("Email", validators=DefaultFormValidators.new_email)
    new_username = StringField("Username", validators=DefaultFormValidators.new_username)
    new_password = PasswordField("Password", validators=DefaultFormValidators.new_password)


