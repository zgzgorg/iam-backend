"""Account API modules"""
import logging
import datetime
import http
import sqlalchemy.exc
import flask_restx


import zgiam.api.lib
import zgiam.lib.log
import zgiam.database
import zgiam.models
import zgiam.api


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
        "phone_number": flask_restx.fields.String(example="1234567890", required=True),
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
    def post(self):
        """register user and insert data to database"""
        zgiam.api.lib.validate_payload(_account_api_v1.payload, _account)

        account_kwargs = _account_api_v1.payload.copy()
        try:
            account_kwargs["join_date"] = datetime.date.fromisoformat(account_kwargs["join_date"])
        except KeyError:
            account_kwargs["join_date"] = datetime.date.today()

        try:
            account_kwargs["birthday"] = datetime.date.fromisoformat(account_kwargs["birthday"])
        except KeyError:
            ...

        account = zgiam.models.Account(**account_kwargs)
        db = zgiam.database.get_db()
        try:
            db.session.add(account)  # pylint: disable=no-member
            db.session.commit()  # pylint: disable=no-member
        except sqlalchemy.exc.IntegrityError as e:
            logger.error("database commit error: %s", e)
            flask_restx.abort(http.HTTPStatus.CONFLICT)
