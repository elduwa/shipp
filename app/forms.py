from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, IPAddress, MacAddress, Email, Length, Regexp, EqualTo, ValidationError
from app.models.database_model import User
from extensions import db


class DeviceForm(FlaskForm):
    name = StringField('Device Name', validators=[DataRequired()])
    mac = StringField('MAC Address', validators=[DataRequired(), MacAddress()])
    ip = StringField('IP Address', validators=[DataRequired(), IPAddress()])


class LoginForm(FlaskForm):
    email = StringField('Your email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                                                         'Usernames must have only '
                                                                                         'letters, numbers, '
                                                                                         'dots or underscores')])
    password = PasswordField('Password', validators=[DataRequired(),
                                                     EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])

    def validate_email(self, field):
        if db.session.execute(db.select(User).where(User.email == field.data)).scalars().first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if db.session.execute(db.select(User).where(User.username == field.data)).scalars().first():
            raise ValidationError('Username already in use.')
