from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp, ValidationError
from models.user import User

class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=2, message="Name must be at least 2 characters long"),
        Regexp(r'^[A-Za-z\s]+$', message="Name must contain only letters and spaces")
    ])
    email = StringField('Email Address', validators=[
        DataRequired(),
        Regexp(
            r'^[a-zA-Z0-9._+-]+@focus-corporation\.com$',
            message="Please enter a valid focus-corporation.com email address"
        )
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message="Password must be at least 6 characters long"),
        Regexp(r'(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>])',
               message="Password must contain uppercase, lowercase, numbers, and special characters")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message="Passwords must match")
    ])
    submit = SubmitField('Register')

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError('Email address is already registered.')