"""
sla_checker PYPI setup file.

Install with: python3 setup.py install
Develop with: python3 setup.py develop
Make it available on PIP with:
    python3 setup.py sdist
    pip3 install twine
    twine upload dist/*
"""
__author__ = "Andrea Dainese"
__contact__ = "andrea@adainese.it"
__copyright__ = "Copyright 2022, Andrea Dainese"
__license__ = "GPLv3"
__version__ = "0.0.3"

from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="sla_checker",
    version=__version__,
    description="A python module that will check if two events are within a defined SLA.",
    url="https://github.com/dainok/sla_checker",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Andrea Dainese",
    author_email="andrea@adainese.it",
    license="GNU v3.0",
    install_requires=[
        "holidays==0.25",
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
    ],
    project_urls={
        "Source": "https://github.com/dainok/sla_checker",
    },
    python_requires=">=3.6",
)
