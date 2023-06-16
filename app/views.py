# App routing
from flask import Blueprint, render_template, redirect, url_for
from app.extensions import db
from app.models.database_model import Device, DeviceConfig, Policy
from app.forms import DeviceForm
from datetime import datetime

bp = Blueprint("main", __name__, template_folder="templates")


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/devices")
def devices():
    active_devices = db.session.execute(db.select(
        Device.id, Device.device_name, Device.mac_address, DeviceConfig.ip_address, DeviceConfig.valid_from)
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
        return redirect(url_for("main.devices"))
    return render_template("add-device.html", form=form)


@bp.route("/edit-device/<int:device_id>", methods=["GET", "POST"])
def edit_device(device_id):
    device = db.get_or_404(Device, device_id)
    current_config = device.get_current_config()
    form = DeviceForm()
    if form.validate_on_submit():
        device.device_name = form.name.data
        device.mac_address = form.mac.data
        if current_config.ip_address != form.ip.data:
            current_config.valid_to = datetime.now()
            current_config.update_device_config()
            device.device_configs.append(DeviceConfig(ip_address=form.ip.data))
        device.update_device()
        return redirect(url_for("main.devices"))
    form.name.data = device.device_name
    form.mac.data = device.mac_address
    form.ip.data = current_config.ip_address
    return render_template("edit-device.html", form=form)
