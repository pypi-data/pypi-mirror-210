#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from os import path

from setuptools import setup, find_packages

this_directory = path.abspath(path.dirname(__file__))

setup(
    name='indecro',
    description='Python scheduler with task independency from scheduler, executor and others',
    version='0.132',
    url='https://github.com/TypeHintsFun/indecro',
    author='TypeHintsFun',
    author_email='typehintsfun@gmail.com',
    license='MIT',
    classifiers=[
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    packages=find_packages(include=['indecro', 'indecro.*']),
    install_requires=[
    ],
    extras_require={
    },
    package_data={
    },
    python_requires=">=3.9",

    long_description=open('README.md').read(),
    long_description_content_type='text/markdown'
)
