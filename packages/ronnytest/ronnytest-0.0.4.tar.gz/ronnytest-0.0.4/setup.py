import setuptools
from setuptools.command.install import install
import os

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        # print('请检查pip指令是否有使用--index-url强制下载内部源,禁止非私有源的外部同名包！'.encode('utf-8').decode('latin1'))
        os.system("cat ronnytest.egg-info/PKG-INFO")

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="ronnytest",
  version="0.0.4",
  author="wxpay_sec_team",
  author_email="wxpay_sec_team@tencent.com",
  description="ronnytest",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/pypi/ronnytest",
  packages=setuptools.find_packages(),
  cmdclass={
        'install': PostInstallCommand,
      },
  classifiers=[
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  ],
)

print('test')