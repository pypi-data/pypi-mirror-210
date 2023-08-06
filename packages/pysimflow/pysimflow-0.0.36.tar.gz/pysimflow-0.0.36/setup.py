#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pysimflow',
    version='0.0.36',
    author='sl.truman',
    author_email='sl.truman@live.com',
    url='',
    description=u'',
    packages=['digitaltwin'],
    install_requires=[
        'numpy',
        'pybullet',
        'scipy'
    ]
)
