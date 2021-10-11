"""testing for zgiam.api.account module"""
# pylint: disable=C0116,W0621,W0212,W0611
import json
import pytest

import zgiam.core
import zgiam.api
import zgiam.database
from tests.mocks.mock_app import app  # noqa: F401


@pytest.fixture
def client(app):
    zgiam.api.register_blueprint()
    with app.test_client() as client:
        yield client


def test_badrequest_account(client):
    response = client.post(
        "/api/v1/account/register",
        data=json.dumps({}),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400


def test_register_account(client):
    response = client.post(
        "/api/v1/account/register",
        data=json.dumps(
            {
                "email": "email1@domain.com",
                "first_name": "Jack",
                "last_name": "Wong",
                "phone_number": "123",
            }
        ),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 200


def test_duplicate_register_account(client):
    for _ in range(2):
        response = client.post(
            "/api/v1/account/register",
            data=json.dumps(
                {
                    "email": "email1@domain.com",
                    "first_name": "Jack",
                    "last_name": "Wong",
                    "phone_number": "123",
                }
            ),
            headers={"Content-Type": "application/json"},
        )
    assert response.status_code == 409
