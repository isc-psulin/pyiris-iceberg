#!/usr/bin/env python
from setuptools import find_packages
from distutils.core import setup     

setup(name='irisiceberg',
      version='1.0',
      description='IRIS Iceberg library',
      author='Patrick Sulin',
      author_email='psulin@intersystems.com',
      url='',
      package_dir={'':'src', 'tests': 'tests'},
      packages=(find_packages(where="src")+['tests', 'tests.unit', 'tests.integration', 'tests.fixtures']),
      install_requires= ['pytest', 'sqlalchemy-iris==0.12.0' ,'pyarrow', 'pandas',
                        'loguru',
                        'pyiceberg',
                        'pydantic',
                        'pydantic_settings',
                        'sqlalchemy']
)