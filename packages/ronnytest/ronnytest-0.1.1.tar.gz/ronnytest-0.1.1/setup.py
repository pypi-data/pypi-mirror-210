'''
Author: ronnyrzyang
Date: 2023-05-15 19:30:45
LastEditors: ronnyrzyang@tencent.com
LastEditTime: 2023-05-25 10:43:46
FilePath: /ronnyrzyang/upload_pypi/ronnytest/setup.py
Description: 
'''
import setuptools
from setuptools.command.install import install as _install

# from pip.commands.install import logger

with open("README.md", "r") as fh:
  long_description = fh.read()

# notice = \
#     "[!!!] NOTICE: mynotice"

# class install_with_warning(_install):
#     def run(self):
#         _install.run(self)
#         logger.warning(notice)
#         logger.error(notice)

# logger.error(notice)

setuptools.setup(
  name="ronnytest",
  version="0.1.1",
  author="wxpay_sec_team",
  author_email="wxpay_sec_team@tencent.com",
  description="ronnytest",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/pypi/ronnytest",
  packages=setuptools.find_packages(),
  classifiers=[
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  ],
)

raise RuntimeError('do not install!')