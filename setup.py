#!/usr/bin/env python
#from setuptools import find_packages, setup
from distutils.core import setup, find_packages

setup(name='irisiceberg',
      version='1.0',
      description='IRIS Iceberg library',
      author='Patrick Sulin',
      author_email='psulin@intersystems.com',
      url='',
      package_dir={'irisiceberg':'src', 'tests': 'tests'},
     # packages=['irisiceberg', 'tests'],
      packages=find_packages() + ['tests'],
      include_package_data=True,
      install_requires= []
)