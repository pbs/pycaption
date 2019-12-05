#!/usr/bin/env python
import os
from setuptools import setup, find_packages

README_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'README.rst')

requirements = {
    "package": open('requirements.txt').read().split('\n')
}

requirements.update(all=sorted(set().union(*requirements.values())))

setup(
    name='pycaption',
    version='1.1.0',
    description='Closed caption converter',
    long_description=open(README_PATH).read(),
    author='Tyler Hoyt',
    author_email='tyler.hoyt+pycaption@zefr.com',
    url='https://github.com/zefr-inc/pycaption',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements['package'],
    extras_require=requirements,
    classifiers=[
        'Topic :: Multimedia :: Video',
    ],
    test_suite="tests",
)
