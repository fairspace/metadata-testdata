#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from setuptools import setup

if sys.version_info < (3, 7):
    sys.exit(
        'Python < 3.7 is not supported. You are using Python {}.{}.'.format(
            sys.version_info[0], sys.version_info[1])
    )

here = os.path.abspath(os.path.dirname(__file__))

with open('requirements.txt', 'r') as f:
    required_packages = f.read().splitlines()

setup(
    name='fairspace-metadata-testdata',
    version='0.0.4',
    description="Script to generate test data for Fairspace",
    author="Gijs Kant",
    author_email='gijs@thehyve.nl',
    url='https://github.com/fairspace/metadata-testdata',
    packages=[
        'fairspace_api',
        'metadata_scripts',
        'testdata'
    ],
    entry_points={
        'console_scripts': ['upload_test_data=metadata_scripts.upload_test_data:main',
                            'sparql_query=metadata_scripts.sparql_query:main',
                            'retrieve_view=metadata_scripts.retrieve_view:main'],
    },
    include_package_data=True,
    license="MIT",
    zip_safe=False,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7'
        'Programming Language :: Python :: 3.8'
    ],
    python_requires='>=3.7.0',
    install_requires=required_packages,
    setup_requires=[
        # dependency for `python setup.py bdist_wheel`
        'wheel'
    ]
)
