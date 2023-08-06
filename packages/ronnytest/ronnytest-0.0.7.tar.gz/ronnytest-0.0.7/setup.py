import setuptools
from setuptools.command.install import install as _install

from pip.commands.install import logger


with open("README.md", "r") as fh:
  long_description = fh.read()

notice = \
    "[!!!] NOTICE: mynotice"

class install_with_warning(_install):
    def run(self):
        _install.run(self)
        logger.warning(notice)
        logger.error(notice)

logger.error(notice)

setuptools.setup(
  name="ronnytest",
  version="0.0.7",
  author="wxpay_sec_team",
  author_email="wxpay_sec_team@tencent.com",
  description="ronnytest",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/pypi/ronnytest",
  packages=setuptools.find_packages(),
  cmdclass={'install': install_with_warning},
  classifiers=[
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  ],
)