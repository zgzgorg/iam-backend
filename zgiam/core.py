"""Flask core app module"""
import typing
import logging

import flask

import zgiam.lib.config
import zgiam.lib.log


logger: logging.Logger = zgiam.lib.log.get_logger(__name__)
_APP: typing.Union[flask.Flask, None] = None


def get_app(name: typing.Union[str, None] = None) -> flask.Flask:
    """get the core app

    Args:
        name (str, optional): application name, None will be `__name__`. Defaults to None.

    Returns:
        Flask
    """
    global _APP
    if _APP is None:
        name = name or __name__

        _APP = flask.Flask(name)
        flask_config = zgiam.lib.config.get_config()["FLASK"]  # type: ignore
        _APP.config.update(flask_config)

        # TODO: check encrypt
        _APP.config["ENV"] = (
            "production" if flask_config.getboolean("PRODUCTION") else "development"
        )

    return _APP
