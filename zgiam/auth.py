"""Authorization module"""
import functools
import datetime
import typing
import http
import json
import oauthlib.oauth2.rfc6749.tokens

import sqlalchemy.exc
import flask
import flask_login
import flask_dance.contrib.google
import flask_dance.consumer.storage.sqla
import flask_dance.consumer
import flask_jwt_extended
import flask_restx

import zgiam.core
import zgiam.database
import zgiam.models
import zgiam.lib.log
import zgiam.lib.config

logger = zgiam.lib.log.get_logger(__name__)


def login_oauth_token_check(func: typing.Callable) -> typing.Any:
    """decorator for login oauth token check by config time

    Args:
        func (typing.Callable): function

    Returns:
        typing.Any: return Any
    """

    @functools.wraps(func)
    @flask_login.login_required
    def decorated_view(*args, **kwargs):
        app = zgiam.core.get_app()
        if app.config.get("LOGIN_DISABLED") or flask.request.headers.get("token", default=None):
            return func(*args, **kwargs)

        config = zgiam.lib.config.get_config()
        google_oauth_token_expire_time = config.getint("CORE", "GOOGLE_OAUTH_TOKEN_EXPIRE_TIME")

        db = zgiam.database.get_db()
        query = db.session.query(zgiam.models.OAuth).filter_by(
            account_id=flask_login.current_user.id,
        )
        try:
            oauth = query.one()
        except sqlalchemy.exc.NoResultFound:
            logger.error("cannot find oauth for %s", flask_login.current_user.id)
            return app.login_manager.unauthorized()  # pylint: disable=no-member
        if google_oauth_token_expire_time:
            token_exist_seconds = (datetime.datetime.utcnow() - oauth.created_at).total_seconds()
            if token_exist_seconds > google_oauth_token_expire_time:
                del app.blueprints["google"].token
                flask.session.clear()
                return app.login_manager.unauthorized()  # pylint: disable=no-member
        return func(*args, **kwargs)

    return decorated_view


def config_auth_apps() -> None:
    """config all auth apps"""
    config = zgiam.lib.config.get_config()
    app = zgiam.core.get_app()
    app.before_request(_make_session_permanent)
    login_manager = flask_login.LoginManager(app)
    login_manager.user_loader(_flask_login_user_loader)
    login_manager.request_loader(_flask_login_request_loader)

    domains = json.loads(config.get("CORE", "DOMAINS"))
    # set google hosted_domain
    primary_domain = domains[0]

    google_blueprint = flask_dance.contrib.google.make_google_blueprint(
        scope=["profile", "email"],
        storage=flask_dance.consumer.storage.sqla.SQLAlchemyStorage(
            zgiam.models.OAuth, zgiam.database.get_db().session, user=flask_login.current_user
        ),
        hosted_domain=primary_domain,
        redirect_url=config.get("CORE", "GOOGLE_OAUTH_REDIRECT_URL"),
    )

    flask_dance.consumer.oauth_authorized.connect_via(google_blueprint)(_google_logged_in)
    flask_dance.consumer.oauth_error.connect_via(google_blueprint)(_google_error)
    app.register_blueprint(google_blueprint, url_prefix="/login")

    # we only use JWT for token usage currently
    flask_jwt_extended.JWTManager(app)


def _make_session_permanent():
    # pylint: disable= assigning-non-slot
    flask.session.permanent = True
    flask.session.modified = True


def _flask_login_user_loader(user_id):
    db = zgiam.database.get_db()
    try:
        return db.session.query(zgiam.models.Account).filter_by(id=user_id).one()
    except sqlalchemy.exc.NoResultFound:
        return None


def _flask_login_request_loader(request: flask.Request):
    db = zgiam.database.get_db()
    token = request.headers.get("token")
    try:
        account_token = (
            db.session.query(zgiam.models.AccountToken)
            .filter_by(token=token, expire_time=None)
            .one()
        )
    except sqlalchemy.exc.NoResultFound:
        return None
    return account_token.account


def _google_logged_in(
    blueprint: flask_dance.consumer.OAuth2ConsumerBlueprint,
    token: oauthlib.oauth2.rfc6749.tokens.OAuth2Token,
):
    """create/login local user on successful OAuth login"""
    if not token:
        logger.error("Failed to log in due to no token from Google")
        flask_restx.abort(http.HTTPStatus.UNAUTHORIZED)

    response = blueprint.session.get("/oauth2/v1/userinfo")
    if not response.ok:
        logger.error("Failed to fetch user info from Google")
        flask_restx.abort(http.HTTPStatus.UNAUTHORIZED)
    user_info = response.json()

    # Verify domains
    user_info_email = user_info["email"]

    if not verify_email_domains(user_info_email):
        logger.warning("user login with email(%s) not in the domain list", user_info_email)
        flask_restx.abort(http.HTTPStatus.UNAUTHORIZED)

    # Find account in the database
    account_id = user_info_email.split("@")[0]

    db = zgiam.database.get_db()
    query = db.session.query(zgiam.models.Account).filter_by(id=account_id)
    try:
        account = query.one()
    except sqlalchemy.exc.NoResultFound:
        logger.error("No account found(email: %s)", user_info_email)
        flask_restx.abort(http.HTTPStatus.UNAUTHORIZED)

    # Create or update the oAuth token
    oauth = zgiam.models.OAuth(  # type: ignore
        provider=blueprint.name,
        account_id=account_id,
        provider_user_id=user_info["id"],
        token=token,
    )

    db.session.merge(oauth)
    db.session.commit()

    flask_login.login_user(account)

    # Disable Flask-Dance's default behavior for saving the OAuth token
    return False


def verify_email_domains(email: str) -> bool:
    """verify email with config domains

    Args:
        email (str): a email address

    Returns:
        bool: True is email in the domains. Otherwise False
    """
    config = zgiam.lib.config.get_config()
    domains = json.loads(config.get("CORE", "DOMAINS"))
    for domain in domains:
        if email.endswith(domain):
            return True
    return False


def _google_error(blueprint: flask_dance.consumer.OAuth2ConsumerBlueprint, message, response):
    """notify on OAuth provider error"""
    flask_restx.abort(
        http.HTTPStatus.UNAUTHORIZED,
        message=f"OAuth error from {blueprint.name}!(message={message} response={response})",
    )
