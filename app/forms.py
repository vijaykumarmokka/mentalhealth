from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,DateField,TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    euid = StringField('EUID', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    dob = DateField('Date of Birth', validators=[DataRequired()], format='%Y-%m-%d')
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')
    


    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class InterventionForm(FlaskForm):
    intervention_type = StringField('Intervention Type', validators=[DataRequired()])
    details = TextAreaField('Details', validators=[DataRequired()])
    submit = SubmitField('Add Intervention')