#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re
from setuptools import find_packages, setup


with open("README-PyPI.md", "r", encoding='UTF-8') as f:
    DOCLINES = f.readlines()


with open("cn2int/cn2int.py", "r", encoding='UTF-8') as f:
    VERSION = re.search(r'(\d+)\.(\d+)\.(\d+)', f.read()).group()


def setup_package():
    setup(
        name="cn2int",
        version=VERSION,
        description="Conversion bettwen Chinese number and integer/float",
        long_description="".join(DOCLINES),
        long_description_content_type="text/markdown",
        author="Hecheng Su",
        author_email="2215523266@qq.com",
        url="https://github.com/citysu/cn2int",
        packages=find_packages(),
        python_requires='>=3',
        classifiers=["Programming Language :: Python :: 3"],
    )


if __name__ == '__main__':
    setup_package()
