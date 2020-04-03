#!/usr/bin/env python
import os
from setuptools import setup, find_packages

README_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'README.rst')

dependencies = [
    'beautifulsoup4>=4.8.2',
    'lxml>=3.2.3',
    'cssutils>=0.9.10',
    'future',
    'enum34',
    'six>=1.9.0'
]

setup(
    name='pycaption-od',
    version='1.0.0',
    description='Closed caption converter',
    long_description=open(README_PATH).read(),
    author='OverDrive',
    author_email='ktighe@overdrive.com',
    url='https://github.com/ktighe-od/pycaption-od',
    install_requires=dependencies,
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Topic :: Multimedia :: Video',
    ],
    test_suite="tests",
)
