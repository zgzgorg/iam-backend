"""Config module"""
import typing
import os
import configparser
import logging
import logging.config

from zgiam.lib import DEFAULT_CONFIG_FOLDER
from . import log

logger: logging.Logger = log.get_logger(__name__)

_CONFIG: typing.Union[configparser.ConfigParser, None] = None
_ENV_PREFIX: str = "IAM"


def get_config(reload: bool = False) -> typing.Optional[configparser.ConfigParser]:
    """get config

    Args:
        reload (bool, optional): True reload the config file again. Defaults to False.

    Returns:
        configparser.ConfigParser
    """
    if not _CONFIG or reload:
        _load_config()
    return _CONFIG


def _load_default_config() -> None:
    global _CONFIG
    default_config_file = os.path.join(DEFAULT_CONFIG_FOLDER, "default_iam.cfg")
    _CONFIG = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    _CONFIG.optionxform = str  # type: ignore
    _CONFIG.read(default_config_file)


@typing.no_type_check
def _load_local_config() -> None:
    read_in_config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    read_in_config.optionxform = str
    env_config_path = os.environ.get(f"{_ENV_PREFIX}_CONFIG_PATH", "/etc/zgiam/zgiam.cfg")
    read_in_config.read(env_config_path)
    _CONFIG.update(read_in_config)


@typing.no_type_check
def _load_environ_config() -> None:
    for section in _CONFIG.sections():
        for option in _CONFIG.options(section):
            config_value = _CONFIG.get(section, option)
            environ_value = os.getenv(
                f"{_ENV_PREFIX}_{section.upper()}_{option.upper()}", config_value
            )
            _CONFIG.set(section, option, environ_value)


@typing.no_type_check
def _load_config() -> None:
    _load_default_config()
    _load_local_config()
    _load_environ_config()

    # update logger config
    new_logging_config_path = _CONFIG.get("LOGGING", "CONFIG_PATH")
    if new_logging_config_path:
        logging.config.fileConfig(new_logging_config_path, disable_existing_loggers=False)
        logger.info("Logging format updated")

    #  update debug
    if _CONFIG.getboolean("CORE", "DEBUG", fallback=False) or _CONFIG.getboolean(
        "FLASK", "DEBUG", fallback=False
    ):
        _CONFIG.set("FLASK", "DEBUG", "TRUE")
        _CONFIG.set("CORE", "DEBUG", "TRUE")
        logging.getLogger().setLevel(logging.DEBUG)
        loggers = [
            logging.getLogger(name)
            for name in logging.root.manager.loggerDict  # pylint: disable=E1101
        ]
        for logger_ in loggers:
            logger_.setLevel(logging.DEBUG)
        logger.debug("DEBUG flag set, in debug mode")
