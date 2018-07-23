#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

import versioneer

setup(
    name='workflow',
    packages=['workflow'],
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    include_package_data=True,
    url='https://github.com/vanaoff/workflow',
    license='MIT',
    author='Ivan Héda',
    author_email='ivan.heda@gmail.com',
    install_requires=['azkaban', 'pyyaml', 'gitpython'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest']
)
