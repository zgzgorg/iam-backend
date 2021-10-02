"""This is lib module using for share code"""
import os

DEFAULT_CONFIG_FOLDER: str = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), os.path.normpath("../conf")
)
