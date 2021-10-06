"""testing for zgiam.lib.config module"""
# pylint: disable=C0116,W0621,W0212,W0611
# NOTE: we may already test config in other module
import os
import zgiam.lib.config


def test_load_different_logging_config():
    default_config_path = os.path.join(
        os.path.dirname(zgiam.__file__) + os.path.normpath("/conf/logging.ini")
    )
    os.environ.setdefault("IAM_LOGGING_CONFIG_PATH", default_config_path)
    zgiam.lib.config.get_config()
    os.environ.unsetenv("IAM_LOGGING_CONFIG_PATH")
