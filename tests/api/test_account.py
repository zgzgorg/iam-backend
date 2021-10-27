"""testing for zgiam.api.account module"""
# pylint: disable=C0116,W0621,W0212,W0611
import json
import mock
import googleapiclient.errors
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


def test_get_account_info(app, unittest_data):
    app.config.pop("LOGIN_DISABLED")
    db = zgiam.database.get_db()
    account = unittest_data.account1
    account_token = unittest_data.account_token1
    db.session.add_all([account, account_token])
    db.session.commit()
    with app.test_client() as client:
        response = client.get("/api/v1/account/info", headers={"token": account_token.token})
        assert response.status_code == 200
        assert json.loads(response.data)["email"] == account.email


def test_update_account_info_pass(app, unittest_data):
    app.config.pop("LOGIN_DISABLED")
    db = zgiam.database.get_db()
    account = unittest_data.account1
    account_token = unittest_data.account_token1
    db.session.add_all([account, account_token])
    db.session.commit()
    with app.test_client() as client:
        response = client.patch(
            "/api/v1/account/info",
            data=json.dumps({"first_name": "test_name_change"}),
            headers={"token": account_token.token, "Content-Type": "application/json"},
        )
        assert response.status_code == 200
        assert json.loads(response.data)["first_name"] == "test_name_change"


def test_update_account_info_empty(app, unittest_data):
    app.config.pop("LOGIN_DISABLED")
    db = zgiam.database.get_db()
    account = unittest_data.account1
    account_token = unittest_data.account_token1
    db.session.add_all([account, account_token])
    db.session.commit()
    with app.test_client() as client:
        response = client.patch(
            "/api/v1/account/info",
            data=json.dumps({}),
            headers={"token": account_token.token, "Content-Type": "application/json"},
        )
        assert response.status_code == 200
        assert json.loads(response.data)["email"] == account.email
        assert json.loads(response.data)["first_name"] == account.first_name
        assert json.loads(response.data)["last_name"] == account.last_name
        assert json.loads(response.data)["id"] == account.id


def test_update_account_info_bad_birthday(app, unittest_data):
    app.config.pop("LOGIN_DISABLED")
    db = zgiam.database.get_db()
    account = unittest_data.account1
    account_token = unittest_data.account_token1
    db.session.add_all([account, account_token])
    db.session.commit()
    with app.test_client() as client:
        response = client.patch(
            "/api/v1/account/info",
            data=json.dumps({"birthday": "1970/01/01"}),
            headers={"token": account_token.token, "Content-Type": "application/json"},
        )
        assert response.status_code == 400


def test_update_account_info_bad_database(app, unittest_data):
    app.config.pop("LOGIN_DISABLED")
    db = zgiam.database.get_db()
    account1 = unittest_data.account1
    account_token1 = unittest_data.account_token1
    account2 = unittest_data.account2
    db.session.add_all([account1, account_token1, account2])
    db.session.commit()
    with app.test_client() as client:
        response = client.patch(
            "/api/v1/account/info",
            data=json.dumps({"email": account2.email}),
            headers={"token": account_token1.token, "Content-Type": "application/json"},
        )
        assert response.status_code == 409


@mock.patch("zgiam.lib.google.AdminDirectory")
def test_approve_registers_pass(_, app, unittest_data):
    app.config.pop("LOGIN_DISABLED")
    db = zgiam.database.get_db()
    account1 = unittest_data.account1
    account_token1 = unittest_data.account_token1
    account2 = unittest_data.account2
    expect_id = account2.id
    del account2.id
    db.session.add_all([account1, account_token1, account2])
    db.session.commit()
    with app.test_client() as client:
        response = client.post(
            "/api/v1/account/approve_registers",
            data=json.dumps({"emails": [account2.email]}),
            headers={"token": account_token1.token, "Content-Type": "application/json"},
        )
        assert response.status_code == 200
        assert json.loads(response.data)[-1]["message"] == f"SUCCESS: id: {expect_id}"


@mock.patch("zgiam.lib.google.AdminDirectory")
def test_approve_registers_account_not_found_in_db(_, app, unittest_data):
    app.config.pop("LOGIN_DISABLED")
    db = zgiam.database.get_db()
    account1 = unittest_data.account1
    account_token1 = unittest_data.account_token1
    db.session.add_all([account1, account_token1])
    db.session.commit()
    account2 = unittest_data.account2
    with app.test_client() as client:
        response = client.post(
            "/api/v1/account/approve_registers",
            data=json.dumps({"emails": [account2.email]}),
            headers={"token": account_token1.token, "Content-Type": "application/json"},
        )
        assert response.status_code == 400


@mock.patch("zgiam.lib.google.AdminDirectory")
def test_approve_registers_google_http_error(admin_directory_mock, app, unittest_data):
    admin_directory_mock().users.insert.side_effect = googleapiclient.errors.HttpError(
        resp=mock.Mock(), content=b"this must fail"
    )
    app.config.pop("LOGIN_DISABLED")
    db = zgiam.database.get_db()
    account1 = unittest_data.account1
    account_token1 = unittest_data.account_token1
    account2 = unittest_data.account2
    db.session.add_all([account1, account_token1, account2])
    db.session.commit()
    with app.test_client() as client:
        response = client.post(
            "/api/v1/account/approve_registers",
            data=json.dumps({"emails": [account2.email]}),
            headers={"token": account_token1.token, "Content-Type": "application/json"},
        )
        assert response.status_code == 400
