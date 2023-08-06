# -*- coding: utf-8 -*-
"""
Created on Fri May 26 15:38:08 2023

@author: Senal Fernando
"""

from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
    ]

setup(
      name = 'SenCalculator',
      version = '0.0.1',
      description = 'A very basic Calculator',
      long_description= open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
      url='',
      author = 'Senal Fernando',
      author_email = 'senalshamika@gmail.com',
      License = 'MIT',
      classifiers=classifiers,
      keywords='calculator',
      packages=find_packages(),
      install_requires=['']
      )