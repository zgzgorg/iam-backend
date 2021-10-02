"""
setup
"""
import os
from typing import List
import setuptools  # type: ignore

PACKAGE_NAME = "zgiam"


def get_version() -> str:
    """read version from VERSION file

    Returns:
        str: version
    """
    version = "0.0.0"

    with open(os.path.join(os.path.dirname(__file__), "VERSION"), encoding="utf-8") as version_fh:
        # Get X.Y.Z
        version = version_fh.read().strip()

    return version


def get_install_requires() -> List[str]:
    """Gets a list of required python pacakges from requirements.txt file.

    Returns:
        A list of required python packages.
    """
    with open("requirements.txt", "r", encoding="utf-8") as requirements_fh:
        return [line for line in requirements_fh.read().splitlines() if not line.startswith("#")]


setuptools.setup(
    name=PACKAGE_NAME,
    version=get_version(),
    description="",
    long_description="This is ZGZG IAM backend module",
    url=None,
    author="William Chen",
    author_email="williamc@zgzg.io",
    license="",
    packages=[PACKAGE_NAME],
    # build dependencies
    setup_requires=[],
    # run-time package dependencies
    install_requires=get_install_requires(),
    # data files installed in packages
    package_data={},
    # data files outside package
    data_files=[],
    python_requires=">=3.8",
)
