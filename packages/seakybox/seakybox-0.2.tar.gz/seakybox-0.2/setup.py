#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Seaky
# @Date:   2019/6/25 16:07


import seakybox
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name=seakybox.__title__,
    version=seakybox.__version__,
    author=seakybox.__author__,
    author_email='seaky.cn@gmail.com',
    description=seakybox.__description__,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/sseaky',
    packages=setuptools.find_packages(),
    install_requires=['beautifulsoup4', 'IPy', 'numpy', 'pandas',
                      'psutil', 'PyMySQL', 'requests',
                      'SocksiPy-branch', 'sqlacodegen', 'SQLAlchemy', 'sshtunnel',
                      'urllib3', 'concurrent-log-handler', 'xlrd', 'openpyxl', 'redis', 'lxml'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
