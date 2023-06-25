"""Initialize any app extensions."""
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from cryptography.fernet import Fernet
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
cipher_suite = Fernet(os.getenv('API_SECRET_KEY').encode())
login_manager = LoginManager()
login_manager.login_view = 'main.login'

