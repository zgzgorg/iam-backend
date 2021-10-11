"""testing for zgiam.lib.common module"""
# pylint: disable=C0116,W0621,W0212,W0611
import pytest
import zgiam.lib.common


def test_load_modules_under_this_module():
    zgiam.lib.common.load_modules()


def test_load_modules_string_map():
    zgiam.lib.common.load_modules("os")


def test_load_not_exist_modules():
    with pytest.raises(ModuleNotFoundError):
        zgiam.lib.common.load_modules("foo")


def test_load_modules_with_some_skipt_module():
    zgiam.lib.common.load_modules("importlib", skip_modules=["importlib.util"])
