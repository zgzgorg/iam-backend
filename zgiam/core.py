"""Flask core app module"""
from typing import Union
import logging

from flask import Flask

import zgiam.lib.config
import zgiam.lib.log


logger: logging.Logger = zgiam.lib.log.get_logger(__name__)
_APP: Union[Flask, None] = None


def get_app(name: Union[str, None] = None) -> Flask:
    """get the core app

    Args:
        name (str, optional): application name, None will be `__name__`. Defaults to None.

    Returns:
        Flask
    """
    global _APP
    if _APP is None:
        name = name or __name__

        _APP = Flask(name)
        flask_config = zgiam.lib.config.get_config()["FLASK"]  # type: ignore
        _APP.config.update(flask_config)

        # TODO: check encrypt
        _APP.config["ENV"] = (
            "production" if flask_config.getboolean("PRODUCTION") else "development"
        )
        logger.debug("test")

    return _APP


if __name__ == "__main__":
    app = get_app()
    app.run()
