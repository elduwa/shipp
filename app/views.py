# App routing
from flask import Blueprint, redirect

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return redirect("http://grafana:3000/")
