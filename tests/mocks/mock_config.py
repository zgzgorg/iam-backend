"""mocking for zgiam.lib.config module"""
# pylint: disable=C0116
import typing
import os
import configparser
import pytest
import zgiam.lib.config
import zgiam.core
import zgiam.database


@pytest.fixture
def config() -> typing.Optional[configparser.ConfigParser]:
    set_test_config_env()
    return zgiam.lib.config.get_config()


def set_test_config_env():
    zgiam.core._app = None  # pylint: disable=protected-access
    zgiam.database._db = None  # pylint: disable=protected-access
    zgiam.lib.config._config = None  # pylint: disable=protected-access
    os.environ["IAM_CONFIG_PATH"] = os.path.join(
        os.path.dirname(__file__), os.path.normpath("../iam_test.cfg")
    )
