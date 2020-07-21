#!/usr/bin/env python

from setuptools import setup, find_packages

with open('requirements.txt') as input_stream:
    requirements = [line.strip() for line in input_stream]

setup(
    name="NLPDatasetIO",
    version="0.0.1",
    author="Zulfat Miftahutdinov",
    author_email="zulfatmi@gmail.com",
    description="Not yet",
    long_description="Not yet",
    long_description_content_type="text/markdown",
    url="https://github.com/dartrevan/NLPDatasetIO",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)