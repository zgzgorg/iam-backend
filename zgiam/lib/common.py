"""common module for share library"""
import typing
import pkgutil
import importlib
import os
import inspect

from . import log

logger = log.get_logger(__name__)


def load_modules(
    import_module_name: typing.Union[None, str] = None,
    skip_modules: typing.Union[None, typing.List[str]] = None,
) -> None:
    """Load module under the current folder or all module under this PYTHONPATH, instill modules

    Args:
        import_module_name (typing.Union[None, str], optional): name of module. Defaults to None.
        skip_modules (typing.Union[None, typing.List[str]], optional): skip modules names.
            Defaults to None.
    """
    logger.info("Loading modules...")

    module = None
    if not import_module_name:
        # get the caller module itself
        stack = inspect.stack()[1]
        module = inspect.getmodule(stack[0])
    else:
        # load the first module itself
        module = importlib.import_module(import_module_name)
        logger.info("Loaded module: %s", module.__name__)

    import_module_name = f"{module.__name__}."  # type: ignore

    # check the module is not the folder sytle package / module.
    # TODO: may have better way

    path = (
        [os.path.split(module.__file__)[0]]  # type: ignore
        if os.path.basename(module.__file__) == "__init__.py"  # type: ignore
        else [module.__file__]  # type: ignore
    )

    for _, name, _ in pkgutil.iter_modules(path, prefix=import_module_name):
        if skip_modules and name in skip_modules:
            continue
        module = importlib.import_module(name)
        logger.info("Loaded module: %s", module.__name__)
