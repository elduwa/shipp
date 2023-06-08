# Bundle all sections and expose the Flask APP
from flask import Flask
from config import Config
import logging


def create_app(config: Config):
    app = Flask(__name__)
    app.logger.info('creating app...')
    app.config.from_object(config)

    app.logger.setLevel(logging.INFO)

    from app.extensions import db
    db.init_app(app)

    from app import views
    app.register_blueprint(views.bp)

    return app

