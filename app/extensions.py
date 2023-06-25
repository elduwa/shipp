"""Initialize any app extensions."""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from cryptography.fernet import Fernet
import os

db = SQLAlchemy()
migrate = Migrate()
cipher_suite = Fernet(os.getenv('API_SECRET_KEY').encode())

