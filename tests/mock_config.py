"""mocking for zgiam.lib.config module"""
# pylint: disable=C0116
import typing
import configparser
import pytest
import zgiam.lib.config


@pytest.fixture
def config() -> typing.Optional[configparser.ConfigParser]:
    config_ = zgiam.lib.config.get_config()
    return config_
