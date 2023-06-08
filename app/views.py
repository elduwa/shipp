# App routing
from flask import  Blueprint

bp = Blueprint("main", __name__)


@bp.route("/")
def homepage():
    """View function for Home Page."""
    return "Hello World!"
