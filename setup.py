#!/usr/bin/env python

from distutils.core import setup

setup(name='irisiceberg',
      version='1.0',
      description='IRIS Iceberg library',
      author='Patrick Sulin',
      author_email='psulin@intersystems.com',
      url='',
      package_dir={'irisiceberg':'src', 'tests': 'tests'},
      packages=['irisiceberg', 'tests'],
      include_package_data=True,
      install_requires= []
)