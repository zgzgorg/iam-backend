"""API module"""
import logging

import flask
import flask_restx

import zgiam.lib.log
import zgiam.lib.common
import zgiam.core

logger: logging.Logger = zgiam.lib.log.get_logger(__name__)


api_v1_blueprint: flask.Blueprint = flask.Blueprint("api_v1", __name__, url_prefix="/api/v1")
api_v1: flask_restx.Api = flask_restx.Api(api_v1_blueprint, version="1")


def register_blueprint() -> None:
    """register all blueprint under this module with Flask app"""
    zgiam.lib.common.load_modules()
    app = zgiam.core.get_app()
    app.register_blueprint(api_v1_blueprint)
