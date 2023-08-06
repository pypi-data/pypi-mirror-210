from setuptools import setup,find_packages


def _post_install(setup):
    def _post_actions():
        print('\033[91m*************************************************************************************************************************************\033[0m')
        print('\033[91m*************************************************************************************************************************************\033[0m')
        print("\033[91mWarning: Tencent security team found that you are currently trying to download the company's internal private package from the official source of pypi!!!\033[0m")
        print("\033[91mWarning: According to Tencent's security regulations, you are not allowed to download third-party private packages that have not been evaluated and confirmed for safety, and your downloading behavior has been blocked!!!\033[0m")
        print('\033[91mWarning: Please use company internal repo for private package downloads, For example : pip install your_package_name --index-url=https://mirrors.tencent.com/#/private/pypi.\033[0m')
        print('\033[91m*************************************************************************************************************************************\033[0m')
        print('\033[91m*************************************************************************************************************************************\033[0m')
        raise RuntimeError('do not install!')
    _post_actions()
    return setup

setup(
    name = 'ronnytest',
    version = '0.2.7',
    author = 'wxpay_sec_team',
    author_email = 'wxpay_sec_team@tencent.com',
    packages = find_packages(),
    install_requires=[""],
    tests_require=[],
)

_post_install(setup)