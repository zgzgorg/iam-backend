"""mocking for zgiam.app module"""
# pylint: disable=C0116
import flask
import pytest
import zgiam.core


@pytest.fixture
def app() -> flask.Flask:
    # TODO: replace flask app for https://github.com/pytest-dev/pytest-flask if needed
    return zgiam.core.get_app()
