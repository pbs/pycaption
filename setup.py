#!/usr/bin/env python
import os
from setuptools import setup, find_packages

README_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'README.rst',
)

dependencies = [
    'beautifulsoup4>=4.12.1',
    'lxml>=4.9.1',
    'cssutils>=2.0.0',
]

dev_dependencies = [
    'pytest',
    'pytest-lazy-fixture'
]

transcript_dependencies = [
    'nltk'
]

setup(
    name='pycaption',
    version='2.2.4',
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
    python_requires='>=3.8,<4.0',
    install_requires=dependencies,
    extras_require={
        'dev': dev_dependencies,
        'transcript': transcript_dependencies
    },
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Multimedia :: Video',
    ],
    test_suite="tests",
)
