#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages
from setuptools.command.develop import develop
from subprocess import check_call
import os
import pkg_resources


def read(file_name: str) -> str:
    with open(os.path.join(os.path.dirname(__file__), file_name)) as of:
        return of.read()


def read_requirements(fname):
    return [str(requirement) for requirement in pkg_resources.parse_requirements(read(fname))]


setup_requirements = ["pytest-runner"]


class PostDevelopCommand(develop):
    """Post-installation for development mode."""

    def run(self):
        develop.run(self)

        import sys

        is_pypy = "__pypy__" in sys.builtin_module_names
        if not is_pypy:
            import pip

            pip.main(["install", "-r", "requirements-jupyterlite.txt"])
            check_call(["jupyter", "lite", "build", "--config", "jupyter_lite_config.json"])


setup(
    name="resotocore",
    version="3.5.0",
    description="Keeps all the things.",
    python_requires=">=3.5",
    classifiers=["Programming Language :: Python :: 3"],
    entry_points={"console_scripts": ["resotocore=resotocore.__main__:main"]},
    install_requires=read_requirements("requirements.txt"),
    license="Apache Software License 2.0",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    include_package_data=True,
    packages=find_packages(include=["resotocore", "resotocore.*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=read_requirements("requirements-dev.txt") + read_requirements("requirements-test.txt"),
    url="https://github.com/someengineering/resoto/tree/main/resotocore",
    cmdclass={
        "develop": PostDevelopCommand,
    },
)
