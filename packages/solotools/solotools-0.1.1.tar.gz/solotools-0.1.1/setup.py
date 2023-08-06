#!/usr/bin/env python
# coding: utf-8
#
# Licensed under MIT
#
import setuptools
from solotools import __version__

with open("README.md", "r",encoding="utf8") as fh:
    long_description = fh.read()

setuptools.setup(
    install_requires=['clickhouse-driver>=0.2.6', 'openpyxl>=3.1.2', 'PyMySQL>=1.0.3'],
    version=__version__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    description="SoloTools - 一个简单的工具集合",
    packages=setuptools.find_namespace_packages(include=["solotools", "solotools.*"], ),
    include_package_data=True
)