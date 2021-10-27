"""Flask core app module"""
import typing
import logging

import flask

import zgiam.lib.config
import zgiam.lib.log


logger: logging.Logger = zgiam.lib.log.get_logger(__name__)
_app: typing.Union[flask.Flask, None] = None


def get_app(name: typing.Union[str, None] = None) -> flask.Flask:
    """get the core app

    Args:
        name (str, optional): application name, None will be `__name__`. Defaults to None.

    Returns:
        Flask
    """
    global _app
    if _app is None:
        name = name or __name__
        flask_config = zgiam.lib.config.get_config()["FLASK"]

        # TODO: check encrypt
        flask_config["ENV"] = (
            "production" if flask_config.getboolean("PRODUCTION") else "development"
        )

        _app = flask.Flask(name)
        _app.config.update(flask_config)
        _convert_flask_config_type(_app.config)
    return _app


def _convert_flask_config_type(config):
    for key, value in config.items():
        if isinstance(value, str):
            try:
                config[key] = int(value)
                continue
            except ValueError:
                value = value.lower()
                if value in ["true", "false"]:
                    config[key] = value == "true"
                elif value == "none":
                    config[key] = None
