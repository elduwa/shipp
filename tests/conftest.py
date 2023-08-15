import os
from dotenv import load_dotenv
import pytest
from contextlib import contextmanager


# Context manager to safely close SQLAlchemy sessions and connections
@contextmanager
def session_scope(session):
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@pytest.fixture
def app():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    dotenv_path = os.path.join(base_dir, "test.env")
    load_dotenv(dotenv_path)

    from app import create_app

    app = create_app("test")
    with app.app_context():
        from app.extensions import db
        db.create_all(bind_key=[None, "pihole"])

    yield app

    with app.app_context():
        from app.extensions import db
        with session_scope(db.session):
            metadata = db.metadata
            for table in reversed(metadata.sorted_tables):
                db.session.execute(table.delete())


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
