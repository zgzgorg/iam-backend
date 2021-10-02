"""Database connector"""
from typing import Union

import flask_sqlalchemy
from flask import Flask

import zgiam.lib.config
import zgiam.core


_DB: Union[flask_sqlalchemy.SQLAlchemy, None] = None


def _config_db(app: Flask) -> None:
    config = zgiam.lib.config.get_config()["DATABASE"]  # type: ignore
    # TODO: better mapping
    type_ = config.get("TYPE").lower()
    url = None

    if type_ == "sqlite":
        url = f"sqlite://{config.get('FILE_PATH')}"
    elif type_ == "postgresql":
        url = (
            f"postgresql://{config.get('USER')}:{config.get('PASSWORD')}"
            f"@{config.get('HOST')}/{config.get('DBNAME')}"
        )
    elif type_ == "mysql":
        url = (
            f"mysql+pymysql://{config.get('USER')}:{config.get('PASSWORD')}"
            f"@{config.get('HOST')}/{config.get('DBNAME')}"
        )
    else:
        raise TypeError(
            "Unsupported DB type. Supported types are " "mysql", "postgresql and sqlite"
        )
    app.config["SQLALCHEMY_DATABASE_URI"] = url

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.get("SQLALCHEMY_TRACK_MODIFICATIONS")


def get_db() -> flask_sqlalchemy.SQLAlchemy:
    """get the database connector, require Flask app global has been created

    Returns:
        flask_sqlalchemy.SQLAlchemy
    """
    global _DB
    if not _DB:
        app = zgiam.core.get_app()
        _config_db(app)
        _DB = flask_sqlalchemy.SQLAlchemy(app)
    return _DB
