from setuptools import setup,find_packages
from setuptools.command.install import install
# import logging
# import sys

# logging.basicConfig(stream=sys.stderr, level=logging.INFO)
# logger = logging.getLogger()

# logger.info("do not install!")

setup(
    name = 'ronnytest',
    version = '0.1.7',
    author = 'wxpay_sec_team',
    author_email = 'wxpay_sec_team@tencent.com',
    packages = find_packages(),
    install_requires=[""],
    tests_require=[],
)

raise RuntimeError('do not install!')