"""testing for zgiam.api.auth module"""
# pylint: disable=C0116,W0621,W0212,W0611
import json
import mock
import oauthlib.oauth2.rfc6749.errors
import zgiam.models
import zgiam.database


def test_login_oauth_redirect(client):
    response = client.get("/api/v1/auth/login")
    assert response.status_code == 302


@mock.patch("flask_dance.contrib.google")
def test_logout_revoke_oauth_pass(_, app, client):
    app.blueprints = {"google": type("_", (), {"token": {"access_token": "..."}})}
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 200


@mock.patch("flask_dance.contrib.google")
def test_logout_revoke_oauth_fail(google_mock, app, client):
    google_mock.google.post.side_effect = oauthlib.oauth2.rfc6749.errors.TokenExpiredError
    app.blueprints = {"google": type("_", (), {"token": {"access_token": "..."}})}
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 200


def test_create_token(app, unittest_data):
    app.config.pop("LOGIN_DISABLED")
    db = zgiam.database.get_db()
    account = unittest_data.account1
    db.session.add(account)
    account_token = unittest_data.account_token1
    db.session.add(account_token)
    db.session.commit()
    with app.test_client() as client:
        response = client.post("/api/v1/auth/token", headers={"token": "..."})
        assert response.status_code == 201


def test_delete_good_token(app, unittest_data):
    app.config.pop("LOGIN_DISABLED")
    db = zgiam.database.get_db()
    account = unittest_data.account1
    db.session.add(account)
    account_token = unittest_data.account_token1
    db.session.add(account_token)
    db.session.commit()
    with app.test_client() as client:
        response = client.delete(
            "/api/v1/auth/token",
            data=json.dumps({"token": "..."}),
            headers={"token": "...", "Content-Type": "application/json"},
        )
        assert response.status_code == 200


def test_delete_bad_token(app, unittest_data):
    app.config.pop("LOGIN_DISABLED")
    db = zgiam.database.get_db()
    account = unittest_data.account1
    db.session.add(account)
    account_token = unittest_data.account_token1
    db.session.add(account_token)
    db.session.commit()
    with app.test_client() as client:
        response = client.delete(
            "/api/v1/auth/token",
            data=json.dumps({"token": ".."}),
            headers={"token": account_token.token, "Content-Type": "application/json"},
        )
        assert response.status_code == 400


def test_get_token(app, unittest_data):
    app.config.pop("LOGIN_DISABLED")
    db = zgiam.database.get_db()
    account = unittest_data.account1
    db.session.add(account)
    account_token = unittest_data.account_token1
    db.session.add(account_token)
    db.session.commit()
    with app.test_client() as client:
        response = client.get(
            "/api/v1/auth/token",
            headers={"token": account_token.token, "Content-Type": "application/json"},
        )
        assert json.loads(response.data)["tokens"] == [
            account_token.token for account_token in account.tokens
        ]
        assert response.status_code == 200
