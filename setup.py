#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
xmapper
--------
xmapper is a XML format convert tool.

See https://github.com/xxh840912/xmapper
"""

from setuptools import find_packages
from setuptools import setup

version = '1.0.0'

with open('requirements.txt') as f:
    requires = f.read().strip().split('\n')


setup(
    name="xmapper",
    version=version,
    description='Easy XML format converter',
    long_description=__doc__,
    long_description_content_type='text/x-rst',
    author='Alex xi',
    author_email='alexxi0213@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    url="https://github.com/xxh840912/xmapper",
    install_requires=requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
