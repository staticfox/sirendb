import logging
import logging.config
import os
from pathlib import Path
import traceback

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
import yaml

from sirendb.core.auth import login_manager
from sirendb.core.db import db
from sirendb.core.redis import redis
from sirendb.core.rq import rq
from sirendb.core.strawberry import GraphQLSchema
from sirendb.lib.storage import storage
import sirendb.v1  # noqa


def create_app(config: dict = None):
    try:
        return _create_app(config)
    except Exception as exc:
        traceback.print_exc()
        raise exc


def _create_app(config: dict = None):
    config_file = os.environ.get('FLASK_CONFIG', 'etc/config.yml')

    if config is None:
        config = {}

    if config_file:
        with open(config_file, 'r') as fp:
            cfg_file_data = yaml.safe_load(fp.read())
        config.update(**cfg_file_data)

    # Setup logger first
    logger_yml = Path('etc/logger.yml')
    if logger_yml.is_file():
        with open(Path('etc/logger.yml'), 'r') as fp:
            log_config = yaml.safe_load(fp)
        logging.config.dictConfig(log_config)

    app = Flask('sirendb')
    app.config.update(**config)

    CORS(app)

    db.init_app(app)
    Migrate(
        app=app,
        db=db,
        directory='src/sirendb/migrations',
    )

    login_manager.init_app(app)

    redis.init_app(app)

    rq.init_app(app)
    storage.init_app(app)

    GraphQLSchema.init_app(app)
    app.register_blueprint(sirendb.v1.media.bp)

    return app
