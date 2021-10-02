"""This is logging config and get logging module. Expect all log get from here"""
import os
import logging
import logging.config

from typing import Union

from zgiam.lib import DEFAULT_CONFIG_FOLDER

_IS_DEFAULT_CONFIG_LOAD: bool = False


def _load_default_config() -> None:
    global _IS_DEFAULT_CONFIG_LOAD
    if not _IS_DEFAULT_CONFIG_LOAD:
        logging.config.fileConfig(os.path.join(DEFAULT_CONFIG_FOLDER, "logging.ini"))
    _IS_DEFAULT_CONFIG_LOAD = True


def get_logger(name: Union[str, None] = None) -> logging.Logger:
    """get logging function

    Args:
        name (str, optional): logger name. Defaults to None.

    Returns:
        logging.Logger
    """
    _load_default_config()
    return logging.getLogger(name)
