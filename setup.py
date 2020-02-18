#!/usr/bin/env python
import os
from setuptools import setup, find_packages

README_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'README.rst')
with open('requirements.txt') as f:
    requirements = f.read().splitlines()


setup(
    name='pycaption',
    version='1.2.0',
    description='Closed caption converter',
    long_description=open(README_PATH).read(),
    author='Sebastian Annies',
    author_email='sebastian.annies@castlabs.com',
    url='https://github.com/castlabs/pycaption',
    install_requires=requirements,
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Topic :: Multimedia :: Video',
    ],
    test_suite="tests",
)
