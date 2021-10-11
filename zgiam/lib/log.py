"""This is logging config and get logging module. Expect all log get from here"""
import os
import logging
import logging.config
import typing

from zgiam.lib import DEFAULT_CONFIG_FOLDER

_is_default_config_load: bool = False


def _load_default_config() -> None:
    global _is_default_config_load
    if not _is_default_config_load:
        logging.config.fileConfig(os.path.join(DEFAULT_CONFIG_FOLDER, "logging.ini"))
    _is_default_config_load = True


def get_logger(name: typing.Union[str, None] = None) -> logging.Logger:
    """get logging function

    Args:
        name (str, optional): logger name. Defaults to None.

    Returns:
        logging.Logger
    """
    _load_default_config()
    return logging.getLogger(name)
