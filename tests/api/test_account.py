"""testing for zgiam.api.account module"""
# pylint: disable=C0116,W0621,W0212,W0611
import json

import zgiam.database
import zgiam.models


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


def test_get_account_info(app):
    app.config.pop("LOGIN_DISABLED")
    db = zgiam.database.get_db()
    account = zgiam.models.Account(
        email="william@iam.test", first_name="william", last_name="chen", id="will"
    )
    account_token = zgiam.models.AccountToken(account_id="will", token="...")
    db.session.add_all([account, account_token])
    db.session.commit()
    with app.test_client() as client:
        response = client.get("/api/v1/account/info", headers={"token": "..."})
        assert response.status_code == 200
        assert json.loads(response.data)["email"] == account.email


def test_update_account_info_pass(app):
    app.config.pop("LOGIN_DISABLED")
    db = zgiam.database.get_db()
    account = zgiam.models.Account(
        email="william@iam.test", first_name="william", last_name="chen", id="will"
    )
    account_token = zgiam.models.AccountToken(account_id="will", token="...")
    db.session.add_all([account, account_token])
    db.session.commit()
    with app.test_client() as client:
        response = client.patch(
            "/api/v1/account/info",
            data=json.dumps({"email": "william@iam.test", "first_name": "will"}),
            headers={"token": "...", "Content-Type": "application/json"},
        )
        assert response.status_code == 200
        assert json.loads(response.data)["first_name"] == "will"


def test_update_account_info_empty(app):
    app.config.pop("LOGIN_DISABLED")
    db = zgiam.database.get_db()
    account = zgiam.models.Account(
        email="william@iam.test", first_name="william", last_name="chen", id="will"
    )
    account_token = zgiam.models.AccountToken(account_id="will", token="...")
    db.session.add_all([account, account_token])
    db.session.commit()
    with app.test_client() as client:
        response = client.patch(
            "/api/v1/account/info",
            data=json.dumps({}),
            headers={"token": "...", "Content-Type": "application/json"},
        )
        assert response.status_code == 200
        assert json.loads(response.data)["email"] == account.email
        assert json.loads(response.data)["first_name"] == account.first_name
        assert json.loads(response.data)["last_name"] == account.last_name
        assert json.loads(response.data)["id"] == account.id


def test_update_account_info_bad_birthday(app):
    app.config.pop("LOGIN_DISABLED")
    db = zgiam.database.get_db()
    account = zgiam.models.Account(
        email="william@iam.test", first_name="william", last_name="chen", id="will"
    )
    account_token = zgiam.models.AccountToken(account_id="will", token="...")
    db.session.add_all([account, account_token])
    db.session.commit()
    with app.test_client() as client:
        response = client.patch(
            "/api/v1/account/info",
            data=json.dumps({"birthday": "1970/01/01"}),
            headers={"token": "...", "Content-Type": "application/json"},
        )
        assert response.status_code == 400


def test_update_account_info_bad_database(app):
    app.config.pop("LOGIN_DISABLED")
    db = zgiam.database.get_db()
    account = zgiam.models.Account(
        email="william@iam.test", first_name="william", last_name="chen", id="will"
    )
    account_token = zgiam.models.AccountToken(account_id="will", token="...")
    account2 = zgiam.models.Account(
        email="william2@iam.test", first_name="william2", last_name="chen", id="will2"
    )
    db.session.add_all([account, account_token, account2])
    db.session.commit()
    with app.test_client() as client:
        response = client.patch(
            "/api/v1/account/info",
            data=json.dumps({"email": account2.email}),
            headers={"token": "...", "Content-Type": "application/json"},
        )
        assert response.status_code == 409
