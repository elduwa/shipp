# App routing
from flask import Blueprint, render_template
from app.extensions import db
from app.models.database_model import Device, DeviceConfig, Policy
from app.forms import DeviceForm

bp = Blueprint("main", __name__, template_folder="templates")


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/devices")
def devices():
    active_devices = db.session.execute(db.select(
        Device.device_name, Device.mac_address,DeviceConfig.ip_address, DeviceConfig.valid_from)
                                        .join(Device.device_configs).where(DeviceConfig.valid_to == None))
    return render_template("devices.html", devices=active_devices)


@bp.route("/add-device", methods=["GET", "POST"])
def add_device():
    form = DeviceForm()
    if form.validate_on_submit():
        # Handle form submission
        device = Device(mac_address=form.mac.data, device_name=form.name.data)
        device.device_configs.append(DeviceConfig(ip_address=form.ip.data))
        device.insert_device()
    return render_template("add-device.html", form=form)