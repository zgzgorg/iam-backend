"""testing for zgiam.app module"""
# pylint: disable=C0116,W0621,W0212,W0611
import mock
import zgiam.app


def test_init():
    module = zgiam.app
    with mock.patch.object(module, "main", return_value=42):
        with mock.patch.object(module, "__name__", "__main__"):
            with mock.patch.object(module.sys, "exit") as mock_exit:
                module.init()
                assert mock_exit.call_args[0][0] == 42


@mock.patch("zgiam.core.get_app")
def test_main(mock_get_app_fn):
    zgiam.app.main()
    assert mock_get_app_fn.called
