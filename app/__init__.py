# Bundle all sections and expose the Flask APP
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config


def create_app(config: Config):
    app = Flask(__name__)
    app.config.from_object(config)

    from app import views, models

    app.register_blueprint(views.bp)

    return app

# db_uri = app.config['SQLALCHEMY_DATABASE_URI']
# influxdb_host = app.config['INFLUXDB_HOST']

# move to model (see patterns in documentation) use current_app
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)
