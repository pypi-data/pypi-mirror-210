# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 22:53:13 2023

@author: stefa
"""
from setuptools import setup, find_packages

setup(
    name='lab_utilities',
    version='0.6.0',
    packages=find_packages(),
    license='MIT',
    description='Lab Utilities',
    long_description='Nothing here yet',
    install_requires=[],
    url='https://github.com/stefangolas/lab_utilities.git',
    author='Stefan Golas',
    author_email='stefanmgolas@gmail.com',
    entry_points={
        'console_scripts': [
            'set-lab-email = lab_utilities.email:set_email_env_variables'
        ]
    }
)
