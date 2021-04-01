import pytest

from sirendb.web.flask import create_app


@pytest.fixture(scope='session')
def app():
    app = create_app(
        config_file=None,
        config={
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        }
    )
    yield app


@pytest.fixture
def client(app):
    with app.app_context() as app_context:
        yield app.test_client()
