"""testing for zgiam.api.lib module"""
# pylint: disable=C0116,W0621,W0212,W0611
import flask_restx.namespace
import flask_restx.fields
import pytest
import werkzeug.exceptions
import zgiam.api.lib
import zgiam.api.account


@pytest.fixture
def test_model():
    return flask_restx.namespace.Namespace(__name__).model(
        "test",
        {
            "email": zgiam.api.lib.Email(),
            "name": flask_restx.fields.String(example="Jack", required=True),
            "data": flask_restx.fields.List(flask_restx.fields.String()),
        },
    )


def test_customfield_validate():
    field = zgiam.api.lib.CustomField()
    field.validate(None)


def test_email_validate_pass():
    field = zgiam.api.lib.Email()
    field.required = True
    field.validate("abc@gmail.com")


def test_email_validate_fail_for_required():
    field = zgiam.api.lib.Email()
    field.required = True
    assert field.validate(None) is False


def test_email_validate_fail_with_wrong_format():
    field = zgiam.api.lib.Email()
    field.required = True
    assert field.validate("abc@google") is False


def test_validate_payload_pass(test_model):
    zgiam.api.lib.validate_payload(
        {"email": "abc@gmail.com", "name": "abc", "data": ["1", "2", "3"]}, test_model
    )


def test_validate_payload_fail_for_required(test_model):
    with pytest.raises(werkzeug.exceptions.BadRequest):
        zgiam.api.lib.validate_payload({"email": "abc@gmail.com"}, test_model)


def test_validate_payload_fail_for_unexpect_key(test_model):
    with pytest.raises(werkzeug.exceptions.BadRequest):
        zgiam.api.lib.validate_payload(
            {"email": "abc@gmail.com", "name": "abc", "nickname": "xxx"}, test_model
        )


def test_validate_payload_fail_for_validation(test_model):
    with pytest.raises(werkzeug.exceptions.BadRequest):
        zgiam.api.lib.validate_payload({"email": "abc@gmail", "name": "abc"}, test_model)
