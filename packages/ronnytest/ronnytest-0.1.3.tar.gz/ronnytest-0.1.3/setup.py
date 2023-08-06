from setuptools import setup,find_packages
from setuptools.command.install import install
import warnings
import os


setup(
    name = 'ronnytest',
    version = '0.1.3',
    author = 'wxpay_sec_team',
    author_email = 'wxpay_sec_team@tencent.com',
    packages = find_packages(),
    install_requires=["    Warning--Please-Use-Wxpay-Private-Pip-Source--contact--WXPAY-Secteam--to--solve--the--problem"],
    tests_require=[],
)