from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Length, Email, DataRequired

class SignUpForm(FlaskForm):
    email = StringField(label="email", validators=[DataRequired(), Email(),Length(min=6, max=64)])
    username = StringField(label="username", validators=[DataRequired(), Length(min=2, max=25)])
    password = PasswordField(label="password", validators=[DataRequired(), Length(min=5, max=64)])
    repeat_password = PasswordField(label="repated_password", validators=[DataRequired(), Length(min=5, max=64)])

class LoginForm(FlaskForm):
    email = StringField("email", validators=[Email()])
    password = PasswordField("password", validators=[Length(min=5)])


