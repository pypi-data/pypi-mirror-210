#!/usr/bin/env python

import os

from setuptools import find_packages, setup

__version__ = '1.4'

try:
    if os.environ['GIT_BRANCH'] == 'master':
        __version__ += '.dev' + os.environ['BUILD_NUMBER']
except KeyError:
    pass

setup(
    name='srf-client',
    description='Centre for Sustainable Road Freight - Data Platform client',
    version=__version__,
    packages=find_packages(),
    license='MIT',
    author='James Howe',
    author_email='jmh205@cam.ac.uk',
    maintainer='Centre for Sustainable Road Freight',
    maintainer_email='tech@csrf.ac.uk',
    url='https://data.csrf.ac.uk',
    project_urls={
        'Documentation': 'https://data.csrf.ac.uk/python/docs'
    },
    python_requires='>=3.7',
    install_requires=[
        'attrs >=19.1',
        'CacheControl',
        'immutabledict <3',
        'geopy <3',
        'iso8601',
        'lazy-object-proxy >=1.4, <2',
        'pyhumps >=1.6, <4',
        'requests >=2.22, <3'
    ],
    extras_require={
        'oauth': ['requests-oauthlib <2', 'oauthlib'],
        'pandas': ['numpy', 'pandas>=1.2']
    },
    setup_requires=[
        'pytest-runner <6',
        'flake8 <4',
        'sphinx >=5.2, <6',
        'wheel'
    ],
    tests_require=[
        'flake8-docstrings <2',
        'pydocstyle >=6.1, <7',
        'pytest >=7.2, <8',
        'pytest-cov >=4, <5',
        'pytest-flake8 ==1.1.0',
        'pytest-mock <4',
        'requests-mock >=1.9.2, <2',
        'requests-oauthlib <2'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Natural Language :: English'
    ]
)
