#!/usr/bin/env python
import os
from setuptools import setup, find_packages
from sys import version

README_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'README.rst')

dependencies = [
    'beautifulsoup4>=4.2.1,<4.5.0',
    'lxml>=3.2.3',
    'cssutils>=0.9.10',
    'future',
    'six>=1.9.0'
]

if version[0] == '2':
    dependencies.append('enum34')

setup(
    name='pycaption',
    version='1.1.0',
    description='Closed caption converter',
    long_description=open(README_PATH).read(),
    author='Joe Norton',
    author_email='joey@nortoncrew.com',
    url='https://github.com/pbs/pycaption',
    install_requires=dependencies,
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Topic :: Multimedia :: Video',
    ],
    test_suite="tests",
)
