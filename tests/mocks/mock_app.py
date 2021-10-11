"""mocking for zgiam.app module"""
# pylint: disable=C0116
import flask
import pytest
import zgiam.core
import zgiam.database
import zgiam.models
import tests.mocks.mock_config


@pytest.fixture
def app() -> flask.Flask:
    # TODO: replace flask app for https://github.com/pytest-dev/pytest-flask if needed
    tests.mocks.mock_config.set_test_config_env()
    db = zgiam.database.get_db()
    zgiam.models.base.metadata.create_all(db.engine)
    db.session.commit()  # pylint: disable=E1101
    return zgiam.core.get_app()
