import os
import tempfile
from config import config

import pytest
from app import create_app
# from app.models import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app(config["test"]())
    app.config.update(SQLITE_URI=f'sqlite:///{db_path}')

    # with app.app_context():
    #     init_db()
    #     get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
