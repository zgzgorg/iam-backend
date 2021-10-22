"""testing for zgiam.lib.config module"""
# pylint: disable=C0116,W0621,W0212,W0611
# NOTE: we may already test config in other module
import os
import logging
import zgiam.lib.config


def test_load_different_logging_config():
    zgiam.lib.config._config = None
    default_config_path = os.path.join(
        os.path.dirname(zgiam.__file__) + os.path.normpath("/conf/logging.ini")
    )
    os.environ.setdefault("IAM_LOGGING_CONFIG_PATH", default_config_path)

    zgiam.lib.config.get_config()
    os.environ.unsetenv("IAM_LOGGING_CONFIG_PATH")


def test_sqlalchemy_debug_config():
    zgiam.lib.config._config = None
    os.environ.setdefault("IAM_DATABASE_SQLALCHEMY_DEBUG", "True")
    zgiam.lib.config.get_config()
    loggers = [
        logging.getLogger(name)
        for name in logging.root.manager.loggerDict  # pylint: disable=no-member
        if "sqlalchemy" in name
    ]

    for logger_ in loggers:
        assert logger_.level == logging.DEBUG
    os.environ.unsetenv("IAM_DATABASE_SQLALCHEMY_DEBUG")
