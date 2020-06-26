from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, SubmitField, DateField, TimeField, SelectField
from wtforms.validators import DataRequired, Email, Length, Optional
import email_validator
from datetime import datetime
from config import departments

class CheckinForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2)])
    email = StringField('Email', validators=[DataRequired(), Email(message='Invalid Email'), Length(max=50)])
    submit = SubmitField('Check In')


class CheckoutForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2)])
    email = StringField('Email', validators=[Optional(), Email(message='Invalid Email'), Length(max=50)])
    submit = SubmitField('Check Out')


class AppointmentForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2)])
    email = StringField('Email', validators=[Optional(), Email(message='Invalid Email'), Length(max=50)])
    department = SelectField('Department', choices=departments, validators=[DataRequired()])
    date = DateField('Date', format="%m/%d/%Y", default=datetime.today(), validators=[DataRequired()])
    time = TimeField('Time', format="%-I:%M %p", default=datetime.now(), validators=[DataRequired()])
    submit = SubmitField('Submit')


    




