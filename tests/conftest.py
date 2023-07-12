import os
from dotenv import load_dotenv
import pytest


@pytest.fixture
def app():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    dotenv_path = os.path.join(base_dir, ".env")
    load_dotenv(dotenv_path)

    from app import create_app

    app = create_app("test")
    with app.app_context():
        from app.extensions import db
        db.create_all()

    yield app

    with app.app_context():
        from app.extensions import db
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
