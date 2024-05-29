#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

from setuptools import find_packages, setup


setup(
    name="burp",
    version=0.0.0,
    description="An in memory db with snapshots to json",
    # long_description=open("README.rst", encoding="utf8").read()
    # + "\n\n"
    # + open("CHANGES.rst").read(),
    author="Dhananjay Pai",
    author_email="dhananjay2002pai@gmail.com",
    url="https://github.com/dhananjaypai08/burp/",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=[
    ],
    zip_safe=False,
    license='BSD',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    # Entry points (for CLI functionality)
    # entry_points={
    #     'console_scripts': [
    #     'burp=burp.your_script:main',  # Replace with your script details
    #   ],
    # },
)