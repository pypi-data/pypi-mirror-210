# coding: utf-8

"""
    domian-paas-sdk-python
"""


from setuptools import setup, find_packages  # noqa: H301

NAME = "domain-paas-sdk-python"
VERSION = "1.0.1"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["urllib3 >= 1.15", "six >= 1.10", "certifi", "python-dateutil"]

setup(
    name=NAME,
    version=VERSION,
    description="This template should help get you started developing with python",
    author="dhi",
    author_email="wafe@dhigroup.com",
    url="",
    keywords=["sdk", "python", "domain-paas"],
    install_requires=REQUIRES,
    packages=find_packages(exclude=["test", "tests"]),
    include_package_data=True,
    long_description="""\
    This template should help get you started developing with python
    """
)
