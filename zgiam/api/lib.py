"""API lib module"""
import re
import http
import typing

import flask
import flask_restx


class CustomField(flask_restx.fields.Raw):
    """All custom fields model"""

    def validate(self, value: typing.Any):  # pylint: disable=no-self-use
        """validation function. Expected overwrite

        Args:
            value (typing.Any): Any value
        """
        return type(value)


class Email(CustomField):
    """
    Email field
    """

    __schema_type__ = "string"
    __schema_format__ = "email"
    __schema_example__ = "email@domain.com"

    def validate(self, value):
        email_regex = re.compile(r"\S+@\S+\.\S+")
        if not value:
            return not self.required
        return bool(email_regex.match(value))


class PhoneNumber(CustomField):
    """
    Phone field
    """

    __schema_type__ = "string"
    __schema_format__ = "phone"
    __schema_example__ = "+10000000000;1,1111"

    def validate(self, value):
        phone_regex = re.compile(r"^[\d+;,]+$")
        if not value:
            return not self.required
        return bool(phone_regex.match(value))


def validate_payload(payload: typing.Any, api_model: flask_restx.Model):
    """Validate fields under CustomField Class

    Args:
        payload (typing.Any): response payload
        api_model (flask_restx.Model): API model
    """
    # check if any required fields are missing in payload
    for key in api_model:
        if api_model[key].required and key not in payload:
            flask.abort(http.HTTPStatus.BAD_REQUEST, f"Required field '{key}' field missing")
    # check payload
    for key in payload:
        try:
            field = api_model[key]
        except KeyError:
            flask.abort(
                http.HTTPStatus.BAD_REQUEST,
                f"Validation of '{key}' field. It is unexpected key error",
            )
        if isinstance(field, flask_restx.fields.List):
            field = field.container
            data = payload[key]
        else:
            data = [payload[key]]
        if isinstance(field, CustomField) and hasattr(field, "validate"):
            for i in data:
                if not field.validate(i):
                    flask.abort(http.HTTPStatus.BAD_REQUEST, f"Validation of '{key}' field failed")
