#!/usr/bin/env python
import os
from setuptools import setup, find_packages

README_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'README.rst')

dependencies = [
    'beautifulsoup4>=4.8.1,<4.9',
    'lxml>=3.2.3',
    'cssutils>=0.9.10',
    'future',
    'enum34; python_version < "3.4"',
    'six>=1.9.0'
]

setup(
    name='pycaption',
    version='1.0.4',
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
