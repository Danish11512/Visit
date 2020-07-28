from flask_wtf import FlaskForm 
from config import departments
from wtforms import StringField, PasswordField, SubmitField, ValidationError, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
import sqlalchemy
from ..models import User
from config import roles
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


class RegistrationForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(1, 64), Email()])
    first_name = StringField("First name", validators=[DataRequired()])
    last_name = StringField("Last name", validators=[DataRequired()])
    department = SelectField("Division", choices=departments, validators=[DataRequired()])
    role = SelectField("Role", choices=roles, validators=[DataRequired()])
    is_supervisor = BooleanField('User is a Supervisor')
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            EqualTo("password2", message="Passwords must match"),
            Length(min=8),
        ],
    )
    password2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self, email_field):
        if User.query.filter_by(email=email_field.data.lower()).first():
            raise ValidationError("An account with this email address already exists")
        return True

    def validate_department(self, dep_field):
        if not dep_field.data or dep_field.data == "":
            raise ValidationError("All users must belong to a Department")
        return True

    def validate_password(self, password_field):
        if len(password_field.data) < 8:
            raise ValidationError("Your password must be 8 or more characters")

        has_num = False
        has_capital = False

        for i in password_field.data:
            if i.isdigit():
                has_num = True
            if i.isupper():
                has_capital = True

        if not (has_num or has_capital):
            raise ValidationError(
                "Passwords must contain at least one number and one capital letter"
            )

        if not has_num:
            raise ValidationError("Password must contain at least one number")

        if not has_capital:
            raise ValidationError("Password must contain at least one capital letter")

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
