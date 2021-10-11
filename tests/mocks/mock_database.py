"""mocking for zgiam.database module"""
# pylint: disable=C0116
import flask_sqlalchemy
import pytest

import zgiam.lib.config
import zgiam.models
import tests.mocks.mock_config


@pytest.fixture
def db() -> flask_sqlalchemy.SQLAlchemy:
    # TODO: we are using sqlite memory for database now, but may be replace by
    # https://github.com/jeancochrane/pytest-flask-sqlalchemy
    tests.mocks.mock_config.set_test_config_env()
    _db = zgiam.database.get_db()
    zgiam.models.base.metadata.create_all(_db.engine)
    _db.session.commit()  # pylint: disable=no-member
    yield _db
    _db.session.close()  # pylint: disable=no-member
