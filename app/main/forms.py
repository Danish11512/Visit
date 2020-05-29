from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, SubmitField 
from wtforms.validators import DataRequired, Email, Length

class CheckinForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2)])
    email = StringField('Email')
    submit = SubmitField('Submit')
