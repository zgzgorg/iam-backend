"""mocking for zgiam.database module"""
# pylint: disable=C0116
import typing
import flask_sqlalchemy
import pytest

import zgiam.lib.config
import zgiam.models

_DB: typing.Union[flask_sqlalchemy.SQLAlchemy, None] = None


@pytest.fixture
def db() -> flask_sqlalchemy.SQLAlchemy:
    # TODO: we are using sqlite memory for database now, but may be replace by
    # https://github.com/jeancochrane/pytest-flask-sqlalchemy
    global _DB

    if not _DB:
        app = zgiam.core.get_app()
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        _DB = flask_sqlalchemy.SQLAlchemy(app)
        zgiam.models.BASE.metadata.create_all(_DB.engine)
        _DB.session.commit()  # pylint: disable=E1101
    return _DB
