# Bundle all sections and expose the Flask APP
from flask import Flask
from config import config
import logging
from flask.logging import default_handler


def create_app(config_name: str):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    if config_name == "production":
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(
            app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
        )

    with app.app_context():
        app.logger.setLevel(logging.INFO)

        from app.extensions import db, login_manager
        db.init_app(app)
        db.create_all()
        login_manager.init_app(app)

        logging.getLogger('sqlalchemy').addHandler(default_handler)

        from app import views
        app.register_blueprint(views.bp)

        from app.dashapp.dashboard import init_dashboard
        app = init_dashboard(app)

        return app
