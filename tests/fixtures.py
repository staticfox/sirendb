import os
import secrets
import shutil
import subprocess
import tempfile

from fakeredis import FakeRedis
import pytest

from sirendb.core.db import db as db_
from sirendb.core.redis import redis as redis_
from sirendb.utils.debug import ASSERT
from sirendb.web.flask import create_app


@pytest.fixture(autouse=True)
def redis(app, client):
    yield

    ASSERT(isinstance(redis_.__local, FakeRedis), 'you should be using fakeredis!')

    redis_.flushall()


class DBFixtureNotIncluded:
    pass


@pytest.fixture(scope='session')
def app():
    os.environ['FLASK_CONFIG'] = ''

    app = create_app(
        config={
            'SQLALCHEMY_DATABASE_URI': DBFixtureNotIncluded,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SECRET_KEY': secrets.token_hex(24),
            'RQ_ASYNC': False,
            'RQ_CONNECTION_CLASS': 'fakeredis.FakeRedis',
            'TESTING': True,
            'BIN_DIR': '/app/bin',
            'GEO_BUILD_DIR': '/app/geo/build',

            # 'IMAGE_STORE_TYPE': 'fs',
            # 'IMAGE_STORE_PATH': './images',
            # 'IMAGE_STORE_BASE_URL': 'http://10.120.70.4:3550/media',

            # 'BIN_DIR': '/home/static/projects/sirendb/bin',
            # 'GEO_BUILD_DIR': '/home/static/projects/sirendb/geoapp/build',
            # 'USE_REAL_NGINX': True,
            # 'USE_REAL_CHROME': True,


            'IMAGE_STORE_TYPE': 'test',
            'IMAGE_STORE_BASE_URL': 'http://localhost:5000/media',
            # 'SQLALCHEMY_ECHO': True,
        }
    )
    yield app


@pytest.fixture
def client(app):
    with app.app_context():
        yield app.test_client()


def _run(args):
    subprocess.run(args)  # , stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


@pytest.fixture(scope='session')
def postgresql():
    temp_dir = tempfile.mkdtemp(prefix='sirendb.')

    _run([
        'pg_ctl', 'initdb', '--pgdata', temp_dir
    ])

    _run([
        'pg_ctl', '--pgdata', temp_dir, '--wait', '--options', f'-h "" -k "{temp_dir}"', 'start'
    ])

    _run([
        'createdb', '-h', temp_dir, 'sirendb_test'
    ])

    yield f'postgresql+psycopg2:///sirendb_test?host={temp_dir}'

    try:
        _run([
            'pg_ctl', '-D', temp_dir, '-m', 'immediate', 'stop'
        ])
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
