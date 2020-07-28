from flask_wtf import FlaskForm 
from ..models import User
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
import email_validator
from config import departments, roles


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

class ChangeUserDataForm(FlaskForm):
    first_name = StringField("First name")
    last_name = StringField("Last name")
    role = SelectField("Role", choices=roles, validators=[DataRequired()])
    department = SelectField("Department", choices=departments, validators=[DataRequired()])
    supervisor_id = SelectField(
        "Supervisor Email",
        choices=[(0, "No Supervisor")],
        default=0,
        coerce=int,
        validators=[Optional()],
    )
    is_supervisor = BooleanField("User is a supervisor")
    is_active = BooleanField("User is active")
    submit = SubmitField("Update")

    def validate_supervisor_id(self, id_field):
        """
        Verifies that id used for supervisors exist in the system.
        :param id_field: The supervisor's id
        :return:
        """
        if id_field.data == 0:
            return True
        user = User.query.filter_by(id=id_field.data).first()
        if not user:
            raise ValidationError("No account with that id exists")
