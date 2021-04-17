import logging
import logging.config
import os
from pathlib import Path
from typing import NamedTuple

from flask import (
    Config as Config_,
    Flask as Flask_,
)
from flask_migrate import Migrate
import yaml

from sirendb.core.auth import login_manager
from sirendb.core.db import db
from sirendb.core.redis import redis
from sirendb.core.rq import rq
from sirendb.core.strawberry import GraphQLSchema
from sirendb.lib.storage import storage
import sirendb.v1  # noqa


# class Namespace
# namespaces = {
#     'IMAGE_STORE_': {
#         ''
#     }
# }


class FilesystemConfig(NamedTuple):
    type_: str
    path: str
    base_url: str


class Config(Config_):
    def get_image_store(self):
        cfg = self.get_namespace('IMAGE_STORE_')
        if not cfg:
            return None

        type_ = cfg.get('type', '').lower()

        if type_ == 'fs' and 'base_url' in cfg and 'path' in cfg:
            return FilesystemConfig(
                type_=type_,
                base_url=cfg['base_url'],
                path=cfg['path'],
            )
        else:
            return None


class Flask(Flask_):
    config_class = Config


def create_app(config: dict = None):
    config_file = os.environ.get('FLASK_CONFIG', 'etc/config.yml')

    if config is None:
        config = {}

    if config_file:
        with open(config_file, 'r') as fp:
            cfg_file_data = yaml.safe_load(fp.read())
        config.update(**cfg_file_data)

    app = Flask('sirendb')
    app.config.update(**config)

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

    logger_yml = Path('etc/logger.yml')
    if logger_yml.is_file():
        with open(Path('etc/logger.yml'), 'r') as fp:
            log_config = yaml.safe_load(fp)
        logging.config.dictConfig(log_config)

    GraphQLSchema.init_app(app)

    return app
