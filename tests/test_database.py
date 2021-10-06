"""testing for zgiam.database module"""
# pylint: disable=C0116,W0621,W0212,W0611
import pytest
from mock_database import db  # noqa: F401
from mock_config import config  # noqa: F401
from mock_app import app  # noqa: F401
import zgiam.models
import zgiam.core
import zgiam.lib.config
import zgiam.database


def test_get_db():
    zgiam.database.get_db()


def test_table_create(db):
    zgiam.models.BASE.metadata.create_all(db.engine)


def test_database_sqlite_config(app, config):
    config.set("DATABASE", "TYPE", "sqlite")
    config.set("DATABASE", "FILE_PATH", "/:memory:")
    zgiam.database._config_db(app)
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"
    assert app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]


def test_database_postgresql_config(app, config):
    config.set("DATABASE", "TYPE", "PostgreSQL")
    config.set("DATABASE", "HOST", "localhost")
    config.set("DATABASE", "PORT", "5432")
    config.set("DATABASE", "USER", "admin")
    config.set("DATABASE", "PASSWORD", "admin")
    config.set("DATABASE", "DBNAME", "zgiam")
    zgiam.database._config_db(app)
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "postgresql://admin:admin@localhost:5432/zgiam"
    assert app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]


def test_database_mysql_config(app, config):
    config.set("DATABASE", "TYPE", "mysql")
    config.set("DATABASE", "HOST", "localhost")
    config.set("DATABASE", "PORT", "3306")
    config.set("DATABASE", "USER", "admin")
    config.set("DATABASE", "PASSWORD", "admin")
    config.set("DATABASE", "DBNAME", "zgiam")
    zgiam.database._config_db(app)
    assert (
        app.config["SQLALCHEMY_DATABASE_URI"] == "mysql+pymysql://admin:admin@localhost:3306/zgiam"
    )
    assert app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]


def test_database_wrong_config(app, config):
    config.set("DATABASE", "TYPE", "mongodb")
    config.set("DATABASE", "HOST", "localhost")
    config.set("DATABASE", "PORT", "27019")
    config.set("DATABASE", "USER", "admin")
    config.set("DATABASE", "PASSWORD", "admin")
    config.set("DATABASE", "DBNAME", "zgiam")
    with pytest.raises(TypeError):
        zgiam.database._config_db(app)
