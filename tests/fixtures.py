import tempfile
import secrets
import shutil
import subprocess

import pytest

from sirendb.core.db import db as db_
from sirendb.web.flask import create_app


class DBFixtureNotIncluded:
    pass


@pytest.fixture(scope='session')
def app():
    app = create_app(
        config_file=None,
        config={
            'SQLALCHEMY_DATABASE_URI': DBFixtureNotIncluded,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SECRET_KEY': secrets.token_hex(24),
        }
    )
    yield app


@pytest.fixture
def client(app):
    with app.app_context():
        yield app.test_client()


@pytest.fixture(scope='session')
def postgresql():
    temp_dir = tempfile.mkdtemp(prefix='sirendb.')

    subprocess.run([
        'pg_ctl', 'initdb', '--pgdata', temp_dir
    ], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    subprocess.run([
        'pg_ctl', '--pgdata', temp_dir, '--wait', '--options', f'-h "" -k "{temp_dir}"', 'start'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    subprocess.run([
        'createdb', '-h', temp_dir, 'sirendb_test'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    yield f'postgresql+psycopg2:///sirendb_test?host={temp_dir}'

    try:
        subprocess.run([
            'pg_ctl', '-D', temp_dir, '-m', 'immediate', 'stop'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        shutil.rmtree(temp_dir)


@pytest.fixture(scope='session')
def database(app, postgresql):
    app.config['SQLALCHEMY_DATABASE_URI'] = postgresql

    with app.app_context():
        db_.create_all()

    yield db_

    db_.session.remove()

    with app.app_context():
        db_.drop_all()


@pytest.fixture
def db(database, monkeypatch):
    def flush_with_expire(*args, **kwargs):
        database.session.flush(*args, **kwargs)
        database.session.expire_all()

    monkeypatch.setattr(database.session, 'commit', flush_with_expire)
    monkeypatch.setattr(database.session, 'remove', lambda: None)

    yield database

    database.session.rollback()
    database.session.remove()
