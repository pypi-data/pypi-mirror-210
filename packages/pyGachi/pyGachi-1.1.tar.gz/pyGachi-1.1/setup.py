#!/usr/bin/env python

from io import open
from setuptools import setup

version = '1.1'

setup(
    name='pyGachi',
    author='GachiParty',

    version=version,
    author_email='fetom30268@cutefier.com',

    description=(
        u'Brat ne trogai, eto tibe ne nado'
    ),

    url='https://github.com/DANILYH/pyGachi',
    download_url='https://github.com/DANILYH/pyGachi/archive/v{}.zip'.format(
        version
    ),

    license='Apache License, Version 2.0, see LICENSE file',

    packages=['pyGachi'],
    install_requires=['aiohttp', 'aiofiles'],

    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: CPython',
    ]

)
