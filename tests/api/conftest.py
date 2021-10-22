"""mocking for zgiam module"""
# pylint: disable=C0116
import typing
import pytest


@pytest.fixture
def client(app) -> typing.Generator:
    with app.test_client() as test_client:
        yield test_client
