#!/usr/bin/env python
import os
from setuptools import setup, find_packages

README_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'README.rst')

dependencies = [
    'beautifulsoup4>=4.2.1,<=4.6.0',
    'lxml==3.6.1',
    'cssutils>=1.0.1',
    'future',
    'enum34',
    'six>=1.9.0'
]

setup(
    name='pycaption',
    version='1.1.0.ud4',
    description='Closed caption converter',
    long_description=open(README_PATH).read(),
    author='Joe Norton',
    author_email='joey@nortoncrew.com',
    url='https://github.com/udemy/pycaption',
    install_requires=dependencies,
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Topic :: Multimedia :: Video',
    ],
    test_suite="tests",
)
