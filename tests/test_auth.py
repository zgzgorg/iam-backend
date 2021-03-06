"""testing for zgiam.auth module"""
# pylint: disable=C0116,W0621,W0212,W0611
import datetime

import pytest
import mock
import flask_login
import werkzeug.exceptions
import flask_dance.contrib.google

import zgiam.models
import zgiam.auth
import zgiam.database
import zgiam.lib.config


@pytest.fixture
def flask_dance_sessions():
    return flask_dance.contrib.google.google


def test_login_oauth_token_check_when_login_disable(app):
    app.route("/test")(lambda: "ok")
    with app.test_client() as client:
        client.get("/test")
        assert zgiam.auth.login_oauth_token_check(lambda: "abc")() == "abc"


def test_login_oauth_token_check_pass(app, unittest_data):
    app.config.pop("LOGIN_DISABLED")
    db = zgiam.database.get_db()
    account = unittest_data.account1
    oauth = unittest_data.oauth1
    db.session.add_all([account, oauth])
    db.session.commit()

    @app.route("/test")
    def _():
        flask_login.login_user(account)
        zgiam.auth.login_oauth_token_check(lambda: None)()
        return {"message": "ok"}

    with app.test_client() as client:
        response = client.get("/test")
        assert response.status_code == 200


def test_login_no_oauth_token_check(app, unittest_data):
    app.config.pop("LOGIN_DISABLED")

    db = zgiam.database.get_db()
    account = unittest_data.account1

    db.session.add(account)
    db.session.commit()

    @app.route("/test")
    def _():
        flask_login.login_user(account)
        zgiam.auth.login_oauth_token_check(lambda: None)()
        return {"message": "ok"}

    with app.test_client() as client:
        response = client.get("/test")
        assert response.status_code == 401


def test_login_oauth_token_expired(app, unittest_data):
    app.config.pop("LOGIN_DISABLED")
    db = zgiam.database.get_db()
    config = zgiam.lib.config.get_config()
    google_oauth_token_expire_time = config.getint("CORE", "GOOGLE_OAUTH_TOKEN_EXPIRE_TIME")

    account = unittest_data.account1
    oauth = unittest_data.oauth1
    oauth.created_at = datetime.datetime.utcnow() - datetime.timedelta(
        seconds=google_oauth_token_expire_time + 1
    )
    db.session.add_all([account, oauth])
    db.session.commit()

    @app.route("/test")
    def _():
        flask_login.login_user(account)
        zgiam.auth.login_oauth_token_check(lambda: None)()
        return {"message": "ok"}

    with app.test_client() as client:
        response = client.get("/test")
        assert response.status_code == 401


def test_flask_login_user_loader(db, unittest_data):
    account = unittest_data.account1
    assert not zgiam.auth._flask_login_user_loader(account.id)
    db = zgiam.database.get_db()
    db.session.add(account)
    db.session.commit()
    assert zgiam.auth._flask_login_user_loader(account.id) == account


def test_login_account_token_check_pass(app, unittest_data):
    app.config.pop("LOGIN_DISABLED")
    db = zgiam.database.get_db()
    account = unittest_data.account1
    account_token = unittest_data.account_token1
    db.session.add_all([account, account_token])
    db.session.commit()

    @app.route("/test")
    @flask_login.login_required
    def _():
        return {"message": "ok"}

    with app.test_client() as client:
        response = client.get("/test", headers={"token": account_token.token})
        assert response.status_code == 200


def test_login_account_token_check_fail(app, unittest_data):
    app.config.pop("LOGIN_DISABLED")
    db = zgiam.database.get_db()
    account = unittest_data.account1
    account_token = unittest_data.account_token1
    db.session.add_all([account, account_token])
    db.session.commit()

    @app.route("/test")
    @flask_login.login_required
    def _():
        return {"message": "ok"}

    with app.test_client() as client:
        response = client.get("/test", headers={"token": "it must fail"})
        assert response.status_code == 401


def test_google_error():
    with pytest.raises(werkzeug.exceptions.Unauthorized):
        zgiam.auth._google_error(mock.Mock(), "some message", "some response")


def test_google_logged_in_wrong_domain(db):  # pylint: disable=unused-argument
    blueprint = mock.Mock()
    blueprint.session = mock.Mock()
    blueprint.session.get.return_value = type(
        "_", (), {"json": lambda: {"email": "will@iamwrongdomain.test", "id": "will"}, "ok": True}
    )
    with pytest.raises(werkzeug.exceptions.Unauthorized):
        zgiam.auth._google_logged_in(blueprint, {"token": "..."})


def test_google_logged_in_no_account_in_db(db):  # pylint: disable=unused-argument
    blueprint = mock.Mock()
    blueprint.session = mock.Mock()
    blueprint.session.get.return_value = type(
        "_", (), {"json": lambda: {"email": "william@iam.test", "id": "will"}, "ok": True}
    )
    with pytest.raises(werkzeug.exceptions.Unauthorized):
        zgiam.auth._google_logged_in(blueprint, {"token": "..."})


def test_google_logged_in_no_provider_token():
    blueprint = mock.Mock()
    with pytest.raises(werkzeug.exceptions.Unauthorized):
        zgiam.auth._google_logged_in(blueprint, None)


def test_google_logged_in_response_error():
    blueprint = mock.Mock()
    blueprint.name = "test_blueprint"
    blueprint.session = mock.Mock()
    blueprint.session.get.return_value = type(
        "_", (), {"json": lambda: {"email": "will@iam.test", "id": "12345"}, "ok": False}
    )
    with pytest.raises(werkzeug.exceptions.Unauthorized):
        zgiam.auth._google_logged_in(blueprint, {"token": "..."})


@mock.patch("flask_login.login_user")
def test_google_logged_in_success(_, db, unittest_data):
    account = unittest_data.account1
    db.session.add(account)
    db.session.commit()
    blueprint = mock.Mock()
    blueprint.name = "test_blueprint"
    blueprint.session = mock.Mock()
    blueprint.session.get.return_value = type(
        "_", (), {"json": lambda: {"email": account.email, "id": "12345"}, "ok": True}
    )
    assert not zgiam.auth._google_logged_in(blueprint, {"token": "..."})
