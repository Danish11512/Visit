from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, SubmitField 
from wtforms.validators import DataRequired, Email, Length, EqualTo
import email_validator


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(min=1, max=64), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Old password", validators=[DataRequired()])
    password = PasswordField("New password", validators=[DataRequired(), EqualTo("password2", message="Passwords must match"), Length(min=8)])
    password2 = PasswordField("Confirm new password", validators=[DataRequired()])
    submit = SubmitField("Update Password") 

class PasswordResetForm(FlaskForm):
    password = PasswordField("New Password",validators=[DataRequired(),EqualTo("password2", message="Passwords must match"),],)
    password2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Reset Password")
