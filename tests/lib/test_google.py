"""testing for zgiam.lib.google module"""
# pylint: disable=C0116,W0621,W0212,W0611,C0115
import pytest
import mock

import zgiam.lib.google


def test_google_is_abstract():
    with pytest.raises(TypeError):
        zgiam.lib.google.Google()  # pylint: disable=abstract-class-instantiated


def test_google_no_general_key_in_config(config):
    config.set("GOOGLE_SERVICE_ACCOUNT_KEY_PATH", "GENERAL_KEY", "")

    class Test(zgiam.lib.google.Google):
        def __init__(self, *args, **kwargs):
            super().__init__()

    with pytest.raises(RuntimeError):
        Test()


@mock.patch("google.oauth2.service_account.Credentials.from_service_account_file")
def test_google_admin_directory(
    from_service_account_file_fn_mock, config
):  # pylint: disable=unused-argument
    google_ad_client = zgiam.lib.google.AdminDirectory()
    assert from_service_account_file_fn_mock.called
    assert google_ad_client.users
    assert google_ad_client.groups
