from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, IPAddress, MacAddress


class DeviceForm(FlaskForm):
    name = StringField('Device Name', validators=[DataRequired()])
    mac = StringField('MAC Address', validators=[DataRequired(), MacAddress()])
    ip = StringField('IP Address', validators=[DataRequired(), IPAddress()])

