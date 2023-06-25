from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, IPAddress, MacAddress, Email


class DeviceForm(FlaskForm):
    name = StringField('Device Name', validators=[DataRequired()])
    mac = StringField('MAC Address', validators=[DataRequired(), MacAddress()])
    ip = StringField('IP Address', validators=[DataRequired(), IPAddress()])


class LoginForm(FlaskForm):
    email = StringField('Your email', validators=[DataRequired().Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
