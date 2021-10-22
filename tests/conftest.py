"""mocking for zgiam module"""
# pylint: disable=C0116
import typing
import os
import configparser

import pytest
import flask
import flask_sqlalchemy

import zgiam.core
import zgiam.database
import zgiam.models
import zgiam.auth
import zgiam.api
import zgiam.lib.config


def setup_testing_config_env():
    zgiam.core._app = None  # pylint: disable=protected-access
    zgiam.database._db = None  # pylint: disable=protected-access
    zgiam.lib.config._config = None  # pylint: disable=protected-access
    os.environ["IAM_CONFIG_PATH"] = os.path.join(
        os.path.dirname(__file__), os.path.normpath("iam_test.cfg")
    )


def setup_testing_db():
    _db = zgiam.database.get_db()
    zgiam.models.base.metadata.create_all(_db.engine)
    _db.session.commit()
    return _db


@pytest.fixture
def app() -> flask.Flask:
    # TODO: replace flask app for https://github.com/pytest-dev/pytest-flask if needed
    setup_testing_config_env()
    setup_testing_db()
    zgiam.api.register_blueprint()
    zgiam.auth.config_auth_apps()
    return zgiam.core.get_app()


@pytest.fixture
def config() -> typing.Optional[configparser.ConfigParser]:
    setup_testing_config_env()
    return zgiam.lib.config.get_config()


@pytest.fixture
def db() -> flask_sqlalchemy.SQLAlchemy:
    # TODO: we are using sqlite memory for database now, but may be replace by
    # https://github.com/jeancochrane/pytest-flask-sqlalchemy
    setup_testing_config_env()
    _db = setup_testing_db()
    yield _db
    _db.session.close()
