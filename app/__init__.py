# Bundle all sections and expose the Flask APP
from flask import Flask
from config import Config
import logging
from flask.logging import default_handler


def create_app(config: Config):
    app = Flask(__name__)
    app.config.from_object(config)
    config.init_app(app)

    with app.app_context():
        app.logger.setLevel(logging.INFO)

        from app.extensions import db, login_manager
        db.init_app(app)
        login_manager.init_app(app)

        logging.getLogger('sqlalchemy').addHandler(default_handler)

        from app import views
        app.register_blueprint(views.bp)

        return app
