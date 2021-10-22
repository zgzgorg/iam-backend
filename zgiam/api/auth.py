"""Auth API modules"""
import datetime
import logging
import http
import flask
import flask_restx
import flask_login
import flask_dance.contrib.google
import flask_jwt_extended
import oauthlib.oauth2.rfc6749.errors
import werkzeug.wrappers.response
import sqlalchemy.exc

import zgiam.core
import zgiam.api.lib
import zgiam.lib.log
import zgiam.database
import zgiam.models
import zgiam.api


logger: logging.Logger = zgiam.lib.log.get_logger(__name__)

_auth_api_v1: flask_restx.Namespace = zgiam.api.api_v1.namespace("auth")

_token: flask_restx.Model = _auth_api_v1.model(
    "token", {"token": flask_restx.fields.String(description="API access token")}
)


@_auth_api_v1.route("/login")
class Login(flask_restx.Resource):
    """Login Google OAuth2"""

    @_auth_api_v1.doc(
        description="login account",
        responses={
            int(http.HTTPStatus.UNAUTHORIZED): "unauthorized",
            int(http.HTTPStatus.OK): "login successful",
        },
    )  # pylint: disable=no-self-use
    def post(self) -> werkzeug.wrappers.response.Response:
        """login via google OAuth2"""
        # This is being handle by flask-dance
        return flask.redirect(flask.url_for("google.login"))


@_auth_api_v1.route("/logout")
class Logout(flask_restx.Resource):
    """Logout Google oauth2 and session clear"""

    @_auth_api_v1.doc(
        description="logout account", responses={int(http.HTTPStatus.OK): "logout successful"}
    )  # pylint: disable=no-self-use
    @flask_login.login_required
    def post(self) -> None:
        """logout and clear session"""
        app = zgiam.core.get_app()
        try:
            flask_dance.contrib.google.google.post(
                "https://accounts.google.com/o/oauth2/revoke",
                params={"token": app.blueprints["google"].token["access_token"]},  # type: ignore
                headers={"content-type": "application/x-www-form-urlencoded"},
            )
        except (
            oauthlib.oauth2.rfc6749.errors.TokenExpiredError,
            oauthlib.oauth2.rfc6749.errors.InvalidClientIdError,
        ):
            # oauthlib.oauth2.rfc6749.errors.InvalidClientIdError
            # Our OAuth session apparently expired. We could renew the token
            # and logout again but that seems a bit silly, so for now fake
            # it.
            ...

        del app.blueprints["google"].token  # type: ignore

        flask_login.logout_user()
        flask.session.clear()


@_auth_api_v1.route("/token")
class Token(flask_restx.Resource):
    """Token API"""

    @_auth_api_v1.doc(
        description="get lists of account token",
        responses={int(http.HTTPStatus.OK): "get tokens successful"},
    )  # pylint: disable=no-self-use
    @flask_login.login_required
    def get(self) -> dict:
        """get account token list not expired"""
        account = flask_login.current_user
        tokens = [
            account_token.token for account_token in account.tokens if not account_token.expire_time
        ]
        return {"tokens": tokens}

    @_auth_api_v1.doc(
        description="create account token",
        responses={int(http.HTTPStatus.CREATED): "create token successful with a return token"},
    )  # pylint: disable=no-self-use
    @flask_login.login_required
    @flask_restx.marshal_with(_token)
    def post(self) -> tuple:
        """Create account token"""
        account = flask_login.current_user
        token = flask_jwt_extended.create_access_token(account.id)
        db = zgiam.database.get_db()
        account_token = zgiam.models.AccountToken(account_id=account.id, token=token)
        account.tokens.append(account_token)
        db.session.commit()
        return {"token": token}, http.HTTPStatus.CREATED

    @_auth_api_v1.doc(
        description="create account token",
        responses={
            int(http.HTTPStatus.OK): "delete token successful",
            int(http.HTTPStatus.BAD_REQUEST): "token not found",
        },
    )  # pylint: disable=no-self-use
    @flask_login.login_required
    @_auth_api_v1.expect(_token, validate=True)
    def delete(self) -> None:
        """delete account token"""
        zgiam.api.lib.validate_payload(_auth_api_v1.payload, _token)
        token = _auth_api_v1.payload["token"]
        db = zgiam.database.get_db()
        account = flask_login.current_user
        try:
            account_token = (
                db.session.query(zgiam.models.AccountToken)
                .filter_by(account_id=account.id, token=token, expire_time=None)
                .one()
            )
        except sqlalchemy.exc.NoResultFound:
            flask_restx.abort(http.HTTPStatus.BAD_REQUEST)
        account_token.expire_time = datetime.datetime.now()
        db.session.commit()
