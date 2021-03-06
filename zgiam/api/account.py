"""Account API modules"""
import logging
import datetime
import http

import sqlalchemy.exc
import flask_restx
import flask_login
import googleapiclient.errors

import zgiam.api
import zgiam.api.lib
import zgiam.lib.log
import zgiam.lib.google
import zgiam.database
import zgiam.models
import zgiam.jobs


logger: logging.Logger = zgiam.lib.log.get_logger(__name__)

_account_api_v1: flask_restx.Namespace = zgiam.api.api_v1.namespace("account")

# TODO: use json_schema when marshal support
_account: flask_restx.Model = _account_api_v1.model(
    "account",
    {
        "email": zgiam.api.lib.Email(required=True),
        "first_name": flask_restx.fields.String(example="Jack", required=True),
        "last_name": flask_restx.fields.String(example="Wong", required=True),
        "chinese_name": flask_restx.fields.String(example="王傑克"),
        "nickname": flask_restx.fields.String(example="JJ"),
        "phone_number": zgiam.api.lib.PhoneNumber(example="+10001112222;3,44", required=True),
        "shirt_size": flask_restx.fields.String(example="XXL"),
        "company": flask_restx.fields.String(example="Space X"),
        "school": flask_restx.fields.String(example="Moon College"),
        "dietary_restriction": flask_restx.fields.String(example="No Vag"),
        "reimbursement_platform": flask_restx.fields.String(
            example="paypal", description="can be 'paypal', 'zelle', or 'None'"
        ),
        "reimbursement_method": flask_restx.fields.String(example="email"),
        "reimbursement_phone_number": flask_restx.fields.String(example="1234567890"),
        "reimbursement_email": zgiam.api.lib.Email(),
        "join_date": flask_restx.fields.Date(),
        "birthday": flask_restx.fields.Date(),
        "memo": flask_restx.fields.Wildcard(flask_restx.fields.String, description="json notes"),
        "type": flask_restx.fields.String(example="person", description="can be 'bot' or 'person'"),
    },
)

_approved_account: flask_restx.Model = _account_api_v1.clone(
    "approved_account",
    _account,
    {
        "first_name": flask_restx.fields.String(example="Jack"),
        "last_name": flask_restx.fields.String(example="Wong"),
        "phone_number": zgiam.api.lib.PhoneNumber(example="+10001112222;3,44"),
        "id": flask_restx.fields.String(example="JackW"),
        "email": zgiam.api.lib.Email(),
    },
)

_approving_accounts: flask_restx.Model = _account_api_v1.model(
    "approving_accounts",
    {"emails": flask_restx.fields.List(flask_restx.fields.String, required=True)},
)


@_account_api_v1.route("/register")
class RegisterAccount(flask_restx.Resource):
    """Register Account"""

    @_account_api_v1.doc(
        description="user register",
        responses={
            int(http.HTTPStatus.CONFLICT): "account exists",
            int(http.HTTPStatus.OK): "register account successful",
        },
    )  # pylint: disable=no-self-use
    @_account_api_v1.expect(_account, validate=True)
    def post(self) -> None:
        """register user and insert data to database"""
        zgiam.api.lib.validate_payload(_account_api_v1.payload, _account)

        account_kwargs = _account_api_v1.payload.copy()

        for name in ["first_name", "last_name"]:
            # set format to "Apple Banana"
            account_kwargs[name] = (
                account_kwargs[name][0].upper() + account_kwargs[name][1:].lower()
            )

        try:
            account_kwargs["join_date"] = datetime.date.fromisoformat(account_kwargs["join_date"])
        except KeyError:
            account_kwargs["join_date"] = datetime.date.today()

        try:
            account_kwargs["birthday"] = datetime.date.fromisoformat(account_kwargs["birthday"])
        except KeyError:
            ...

        account = zgiam.models.Account(**account_kwargs)

        try:
            with zgiam.database.get_session() as session:
                session.add(account)
        except sqlalchemy.exc.IntegrityError as e:
            logger.error("database commit error: %s", e)
            flask_restx.abort(http.HTTPStatus.CONFLICT)


@_account_api_v1.route("/info")
class Info(flask_restx.Resource):
    """Account Operation"""

    @_account_api_v1.doc(
        description="Get account infomation",
        responses={int(http.HTTPStatus.OK): "get information successful"},
    )  # pylint: disable=no-self-use
    @flask_restx.marshal_with(_approved_account)
    @flask_login.login_required
    def get(self) -> zgiam.models.Account:
        """get account infomation from database"""
        return flask_login.current_user

    @_account_api_v1.doc(
        description="Update account infomation except `join_date`, `type` and `id`",
        responses={
            int(http.HTTPStatus.OK): "update information successful",
            int(http.HTTPStatus.UNAUTHORIZED): "unauthorized",
            int(http.HTTPStatus.CONFLICT): "email conflict",
        },
    )  # pylint: disable=no-self-use
    @flask_restx.marshal_with(_approved_account)
    @_account_api_v1.expect(_approved_account, validate=True)
    @flask_login.login_required
    def patch(self) -> None:
        """update account infomation"""
        zgiam.api.lib.validate_payload(_account_api_v1.payload, _approved_account)

        avoid_update_field = ["join_date", "type", "id"]
        account_kwargs = {
            key: value
            for key, value in _account_api_v1.payload.items()
            if key not in avoid_update_field
        }

        try:
            account_kwargs["birthday"] = datetime.date.fromisoformat(account_kwargs["birthday"])
        except KeyError:
            ...
        except ValueError:
            flask_restx.abort(http.HTTPStatus.BAD_REQUEST, "wrong birthday format")

        try:
            with zgiam.database.get_session():
                account = flask_login.current_user
                for key, value in account_kwargs.items():
                    setattr(account, key, value)
        except sqlalchemy.exc.IntegrityError:
            flask_restx.abort(http.HTTPStatus.CONFLICT)

        return account


@_account_api_v1.route("/approve_registers")
class ApproveRegisters(flask_restx.Resource):
    """Account Operation"""

    @_account_api_v1.doc(
        description="approve accounts",
        responses={
            int(http.HTTPStatus.OK): "approve accounts successful",
            int(http.HTTPStatus.BAD_REQUEST): "approve accounts have some fails",
        },
    )  # pylint: disable=no-self-use
    @_account_api_v1.expect(_approving_accounts, validate=True)
    @flask_login.login_required
    def post(self) -> list:
        """get account infomation from database"""
        zgiam.api.lib.validate_payload(_account_api_v1.payload, _approving_accounts)
        emails = _account_api_v1.payload["emails"]
        results = []
        has_error = False
        for email in emails:
            message = ""

            try:
                with zgiam.database.get_session() as session:
                    account = session.query(zgiam.models.Account).filter_by(email=email).one()
                    account.generate_id()
                    account.review_by_id = flask_login.current_user.id
                    account.review_status = "APPROVED"
                    zgiam.jobs.create_google_workspace_account(account)
                    # TODO: send welcome email here
                    message = f"SUCCESS: id: {account.id}"
            except sqlalchemy.exc.NoResultFound:
                has_error = True
                message = "ERROR: account not found in database"
            except googleapiclient.errors.HttpError as e:
                has_error = True
                message = f"ERROR: Google Workspace with error({e.error_details})"
            results.append({"email": email, "message": message})
        if has_error:
            flask_restx.abort(http.HTTPStatus.BAD_REQUEST, results)
        return results
