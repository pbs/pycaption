#!/usr/bin/env python
from __future__ import unicode_literals
import os
from setuptools import setup, find_packages

README_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'README.rst')

dependencies = [
    'beautifulsoup4>=4.6.3',
    'lxml>=3.2.3',
    'cssutils>=0.9.10',
    'future',
    'enum34',
    'six>=1.9.0'
]

setup(
    name='le-pycaption',
    version='2.0.0-alpha1',
    description='Closed caption converter',
    long_description=open(README_PATH).read(),
    author='Joe Norton <joey@nortoncrew.com>',
    author_email='blaine@learningequality.org',
    url='https://github.com/learningequality/pycaption',
    license='Apache License, Version 2.0',
    install_requires=dependencies,
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Multimedia :: Video',
    ],
    test_suite="tests",
)
