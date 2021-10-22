"""Config module"""
import typing
import os
import configparser
import logging
import logging.config

from zgiam.lib import DEFAULT_CONFIG_FOLDER
from . import log

logger: logging.Logger = log.get_logger(__name__)

_config: typing.Union[configparser.ConfigParser, None] = None
_ENV_PREFIX: str = "IAM"


def get_config(reload: bool = False) -> typing.Optional[configparser.ConfigParser]:
    """get config

    Args:
        reload (bool, optional): True reload the config file again. Defaults to False.

    Returns:
        configparser.ConfigParser
    """
    if not _config or reload:
        _load_config()
    return _config


def _load_default_config() -> None:
    global _config
    default_config_file = os.path.join(DEFAULT_CONFIG_FOLDER, "default_iam.cfg")
    _config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    _config.optionxform = str  # type: ignore
    _config.read(default_config_file)


@typing.no_type_check
def _load_local_config() -> None:
    read_in_config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    read_in_config.optionxform = str
    env_config_path = os.environ.get(f"{_ENV_PREFIX}_CONFIG_PATH", "/etc/zgiam/zgiam.cfg")
    read_in_config.read(env_config_path)
    for section in _config.sections():
        for option in _config.options(section):
            config_value = _config.get(section, option)
            read_in_config_value = read_in_config.get(section, option, fallback=config_value)
            _config.set(section, option, read_in_config_value)


@typing.no_type_check
def _load_environ_config() -> None:
    for section in _config.sections():
        for option in _config.options(section):
            config_value = _config.get(section, option)
            environ_value = os.getenv(
                f"{_ENV_PREFIX}_{section.upper()}_{option.upper()}", config_value
            )
            _config.set(section, option, environ_value)


@typing.no_type_check
def _load_config() -> None:
    _load_default_config()
    _load_local_config()
    _load_environ_config()

    # update logger config
    new_logging_config_path = _config.get("LOGGING", "CONFIG_PATH")
    if new_logging_config_path:
        logging.config.fileConfig(new_logging_config_path, disable_existing_loggers=False)
        logger.info("Logging format updated")

    #  update debug
    if _config.getboolean("CORE", "DEBUG", fallback=False) or _config.getboolean(
        "FLASK", "DEBUG", fallback=False
    ):
        _config.set("FLASK", "DEBUG", "TRUE")
        _config.set("CORE", "DEBUG", "TRUE")
        root_package_name = __name__.split(".", maxsplit=1)[0]
        logging.getLogger(root_package_name).setLevel(logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)

        loggers = [
            logging.getLogger(name)
            for name in logging.root.manager.loggerDict  # pylint: disable=no-member
            if root_package_name in name
        ]

        for logger_ in loggers:
            logger_.setLevel(logging.DEBUG)

        # Dislike this, but accroding to oauthlib docs only accept environment variables
        # http://oauthlib.readthedocs.org/en/latest/oauth2/security.html
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "True"
        os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "True"
        logger.debug("DEBUG flag set, in debug mode")

    # update sqlalchemy logging debug flag
    if _config.getboolean("DATABASE", "SQLALCHEMY_DEBUG", fallback=False):
        # FIXME: I don't know how to only set sqlalchemy to debug
        #        because the sqlalchemy will folk the root logger
        logging.getLogger().setLevel(logging.DEBUG)
        loggers = [
            logging.getLogger(name)
            for name in logging.root.manager.loggerDict  # pylint: disable=no-member
            if "sqlalchemy" in name
        ]

        for logger_ in loggers:
            logger_.setLevel(logging.DEBUG)

        logger.debug("SQLALCHEMY_DEBUG flag set, sqlalchemy will output debug logging")
