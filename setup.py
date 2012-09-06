#!/usr/bin/env python
import os
from setuptools import setup, find_packages

README_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                           'README.md')

dependencies = [
    'nltk',
    'beautifulsoup4',
    'lxml',
    'cssutils',
    'numpy'
]

setup(
    name='pycaption',
    version='0.2.4',
    description='Closed caption converter',
    author='Joe Norton',
    author_email='joey@nortoncrew.com',
    url='https://github.com/pbs/pycaption',
    install_requires = dependencies,
    packages = find_packages(),
    include_package_data=True,
    classifiers=[
        'Topic :: Multimedia :: Video',
    ],
)
