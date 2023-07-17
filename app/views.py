# App routing
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from app.extensions import db
from app.models.database_model import Device, DeviceConfig, User, Policy
from app.forms import DeviceForm, LoginForm, RegistrationForm
from datetime import datetime
from flask_login import login_required, login_user, logout_user
from app.constants import PolicyType, DefaultPolicyValues
from app.service_integration_api import init_pihole_device, update_pihole_device

bp = Blueprint("main", __name__, template_folder="templates")


@bp.route("/")
def index():
    forwarded_proto = request.headers.get("X-Forwarded-Proto", request.scheme)
    forwarded_host = request.headers.get("X-Forwarded-Host", request.host)
    base_url = f"{forwarded_proto}://{forwarded_host}"
    return redirect(base_url + "/dash/")


@bp.route("/devices")
@login_required
def devices():
    active_devices = db.session.execute(db.select(
        Device.id, Device.device_name, Device.mac_address, DeviceConfig.ip_address, DeviceConfig.valid_from)
                                        .join(Device.device_configs).where(DeviceConfig.valid_to == None))  # noqa: E711
    return render_template("devices.html", devices=active_devices)


@bp.route("/add-device", methods=["GET", "POST"])
@login_required
def add_device():
    form = DeviceForm()
    if form.validate_on_submit():
        # Handle form submission
        device = Device(mac_address=form.mac.data, device_name=form.name.data)
        device.device_configs.append(DeviceConfig(ip_address=form.ip.data))
        default_policy = Policy(policy_type=PolicyType.DEFAULT_POLICY.value,
                                policy_value=DefaultPolicyValues.ALLOW_ALL.value)
        device.policies.append(default_policy)
        device.insert_device()
        try:
            init_pihole_device(device)
        except Exception as e:
            current_app.logger.error(f"Error while initializing pihole device: {e}", "error")
        finally:
            return redirect(url_for("main.devices"))
    return render_template("add-device.html", form=form)


@bp.route("/edit-device/<int:device_id>", methods=["GET", "POST"])
@login_required
def edit_device(device_id):
    device = db.get_or_404(Device, device_id)
    current_config = device.get_current_config()
    form = DeviceForm()
    disable_input_field(form.mac)
    if form.validate_on_submit():
        device.device_name = form.name.data
        if current_config.ip_address != form.ip.data:
            current_config.valid_to = datetime.now()
            current_config.update_device_config()
            device.device_configs.append(DeviceConfig(ip_address=form.ip.data))
        device.update_device()
        try:
            update_pihole_device(device, current_config)
        except Exception as e:
            current_app.logger.error(f"Error while updating pihole device: {e}", "error")
        finally:
            return redirect(url_for("main.devices"))
    form.name.data = device.device_name
    form.mac.data = device.mac_address
    form.ip.data = current_config.ip_address
    return render_template("edit-device.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.execute(db.select(User).where(User.email_address == form.email.data)).scalars().first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next_page = request.args.get("next")
            if next_page is None or not next_page.startswith("/"):
                return redirect(url_for("main.index"))
            return redirect(next_page)
        flash("Invalid username or password.")
    return render_template("login.html", form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email_address=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        user.insert_user()
        return redirect(url_for("main.login"))
    return render_template("register.html", form=form)


def disable_input_field(input_field):
    if input_field.render_kw is None:
        input_field.render_kw = {}
    input_field.render_kw["disabled"] = "disabled"