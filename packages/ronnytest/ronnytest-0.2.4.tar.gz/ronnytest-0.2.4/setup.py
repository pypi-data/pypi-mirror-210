# -*- coding: utf-8 -*-
from __future__ import print_function

import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
from setuptools import setup,find_packages


def _post_install(setup):
    def _post_actions():
        print('\033[91m*************************************************************************************************************************************\033[0m')
        print('\033[91m*************************************************************************************************************************************\033[0m')
        print('\033[91mWarning:腾讯安全团队发现您当前试图从pypi官方源下载公司内部的私有包！\033[0m')
        print('\033[91mWarning:按照腾讯公司安全规范，不得下载未经安全评估和确认的第三方私有包，已阻止您本次下载行为!\033[0m')
        print('\033[91mWarning:请使用pip install your_package_name --index-url=https://mirrors.tencent.com/#/private/pypi 强制指定公司内部源进行私有包下载！\033[0m')
        print('\033[91m*************************************************************************************************************************************\033[0m')
        print('\033[91m*************************************************************************************************************************************\033[0m')
        raise SystemExit
    _post_actions()
    return setup

setup(
    name = 'ronnytest',
    version = '0.2.4',
    author = 'wxpay_sec_team',
    author_email = 'wxpay_sec_team@tencent.com',
    packages = find_packages(),
    install_requires=[""],
    tests_require=[],
)

_post_install(setup)