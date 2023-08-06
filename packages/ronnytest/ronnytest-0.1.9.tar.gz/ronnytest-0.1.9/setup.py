from setuptools import setup,find_packages
from setuptools.command.install import install

def _post_install(setup):
    def _post_actions():
        raise RuntimeError('do not install!')
    _post_actions()
    return setup

setup(
    name = 'ronnytest',
    version = '0.1.9',
    author = 'wxpay_sec_team',
    author_email = 'wxpay_sec_team@tencent.com',
    packages = find_packages(),
    install_requires=[""],
    tests_require=[],
)

_post_install(setup)