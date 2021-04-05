import logging
import logging.config
from pathlib import Path

from flask import Flask
import yaml

from sirendb.core.auth import login_manager
from sirendb.core.db import db
from sirendb.core.strawberry import GraphQLSchema
import sirendb.v1


def create_app(config_file: str = 'etc/config.yml', config: dict = None):
    if config is None:
        config = {}

    if config_file is not None:
        with open(config_file, 'r') as fp:
            cfg_file_data = yaml.safe_load(fp.read())
        config.update(**cfg_file_data)

    app = Flask('sirendb')
    app.config.update(**config)
    db.init_app(app)
    login_manager.init_app(app)

    logger_yml = Path('etc/logger.yml')
    if logger_yml.is_file():
        with open(Path('etc/logger.yml'), 'r') as fp:
            log_config = yaml.safe_load(fp)
        logging.config.dictConfig(log_config)

    GraphQLSchema.init_app(app)

    return app
