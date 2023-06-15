# App routing
from flask import Blueprint, render_template

bp = Blueprint("main", __name__, template_folder="templates")


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/devices")
def devices():
    return render_template("devices.html")