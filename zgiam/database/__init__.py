"""Database connector"""
import typing
import contextlib

import sqlalchemy.orm
import flask_sqlalchemy
import flask

import zgiam.lib.config
import zgiam.core


_db: typing.Union[flask_sqlalchemy.SQLAlchemy, None] = None


def _config_db(app: flask.Flask) -> None:
    config = zgiam.lib.config.get_config()["DATABASE"]  # type: ignore
    # TODO: better mapping
    type_ = config.get("TYPE").lower()
    url = None

    if type_ == "sqlite":
        url = f"sqlite://{config.get('FILE_PATH')}"
    elif type_ == "postgresql":
        url = (
            f"postgresql://{config.get('USER')}:{config.get('PASSWORD')}"
            f"@{config.get('HOST')}:{config.get('PORT')}/{config.get('DBNAME')}"
        )
    elif type_ == "mysql":
        url = (
            f"mysql+pymysql://{config.get('USER')}:{config.get('PASSWORD')}"
            f"@{config.get('HOST')}:{config.get('PORT')}/{config.get('DBNAME')}"
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
    global _db
    if not _db:
        app = zgiam.core.get_app()
        _config_db(app)
        _db = flask_sqlalchemy.SQLAlchemy(app)
    return _db


@contextlib.contextmanager
def get_session(
    session: sqlalchemy.orm.scoped_session = None, *, close: bool = False
) -> typing.Generator:
    """session auto rollback

    Args:
        session (sqlalchemy.orm.scoped_session, optional): sqlalchemy session.
            Defaults to flask_sqlalchemy.SQLAlchemy.Session
        close (bool, optional): close session after use. Defaults to False.

    Returns:
        typing.Generator: SQLAlchemy session

    Yields:
        Iterator[typing.Generator]: SQLAlchemy session
    """
    if not session:
        session = get_db().session
    try:
        yield session
        session.commit()  # type: ignore
    except:  # noqa: E722
        session.rollback()  # type: ignore
        raise
    finally:
        if close:
            session.close()  # type: ignore
