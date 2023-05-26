# Bundle all sections and expose the Flask APP
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config, config
import os

app = Flask(__name__)

if os.getenv('FLASK_ENV') == 'production':
    app.config.from_object(config['production'])
else:
    app.config.from_object(config['development'])

db_uri = app.config['SQLALCHEMY_DATABASE_URI']
influxdb_host = app.config['INFLUXDB_HOST']

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models
