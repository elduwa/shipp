# App routing
from flask import render_template, Blueprint

bp = Blueprint("main", __name__)


@bp.route("/")
def homepage():
    """View function for Home Page."""
    return "Hello World!"
