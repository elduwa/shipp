from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, RadioField
from wtforms.validators import DataRequired, IPAddress, MacAddress, Email, Length, Regexp, EqualTo, ValidationError
from app.models import User
from app.extensions import db
from app.constants import DefaultPolicyValues


class DeviceForm(FlaskForm):
    name = StringField('Device Name', validators=[DataRequired()])
    mac = StringField('MAC Address', validators=[DataRequired(), MacAddress()])
    ip = StringField('IP Address', validators=[DataRequired(), IPAddress()])
    default_policy = RadioField('Default Policy', choices=[(DefaultPolicyValues.ALLOW_ALL.value, 'Allow all'), (DefaultPolicyValues.BLOCK_ALL.value, 'Block all')],
                                default=DefaultPolicyValues.ALLOW_ALL.value, validators=[DataRequired()])



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
        if db.session.execute(db.select(User).where(User.email_address == field.data)).scalars().first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if db.session.execute(db.select(User).where(User.username == field.data)).scalars().first():
            raise ValidationError('Username already in use.')


class UserSettingsForm(FlaskForm):
    pihole_domain = StringField('Pi-hole Domain', validators=[DataRequired()], default='pi.hole')
    pihole_api_token = StringField('Pi-hole API Token', validators=[DataRequired()])