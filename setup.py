#!/usr/bin/env python
import os
from setuptools import setup, find_packages

README_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'README.rst')

dependencies = [
    'nltk==2.0.4',
    'beautifulsoup4==4.2.1',
    'lxml==3.2.3',
    'cssutils==0.9.10',
    'numpy==1.7.1'
]

setup(
    name='pycaption',
    version='0.2.12',
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
