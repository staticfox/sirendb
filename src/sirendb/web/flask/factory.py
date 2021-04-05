import logging
import logging.config
from pathlib import Path

from flask import Flask
from strawberry.flask.views import GraphQLView
import yaml

from sirendb.core.auth import login_manager
from sirendb.core.db import db
from sirendb.core.strawberry import create_schema
import sirendb.graphql
from sirendb.v1 import auth_endpoints


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
    app.register_blueprint(auth_endpoints)
    login_manager.init_app(app)
    login_manager.login_view = 'v1_auth.login'

    logger_yml = Path('etc/logger.yml')
    if logger_yml.is_file():
        with open(Path('etc/logger.yml'), 'r') as fp:
            log_config = yaml.safe_load(fp)
        logging.config.dictConfig(log_config)

    app.add_url_rule(
        '/api/v1/graphql',
        view_func=GraphQLView.as_view('api_v1_graphql_view', schema=create_schema()),
    )

    return app
