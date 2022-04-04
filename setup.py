#!/usr/bin/env python
import os
from setuptools import setup, find_packages

README_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'README.rst',
)

dependencies = [
    'beautifulsoup4>=4.8.1,<4.11',
    'lxml>=4.6.3,<4.9',
    'cssutils>=2.0.0,<2.4',
]

dev_dependencies = [
    'pytest',
    'pytest-lazy-fixture'
]

setup(
    name='pycaption',
    version='2.0.7',
    description='Closed caption converter',
    long_description=open(README_PATH).read(),
    author='Joe Norton',
    author_email='joey@nortoncrew.com',
    project_urls={
        'Source': 'https://github.com/pbs/pycaption',
        'Documentation': 'https://pycaption.readthedocs.io/',
        'Release notes': 'https://pycaption.readthedocs.io'
                         '/en/stable/changelog.html',
    },
    python_requires='>=3.6,<4.0',
    install_requires=dependencies,
    extras_require={
        'dev': dev_dependencies
    },
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Multimedia :: Video',
    ],
    test_suite="tests",
)
