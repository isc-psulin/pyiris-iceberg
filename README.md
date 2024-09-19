# IRIS-ICEBERG
The iris-iceberg library provides utilities for replicating IRIS(SQL) tables into Iceberg tables. It uses the pyiceberg, https://py.iceberg.apache.org/, library to interact with iceberg tables.

This project is meant as an exploration of Iceberg and the PyIceberg library. The primary goal of this exploration is to test replicating IRIS tables into Iceberg tables. The easiest way to test the library is to use the CLI


## Installation
1. git clone git@github.com:isc-patrick/iris-iceberg.git
2. cd iris-iceberg
3. Create and activate a virtualenv
4.  pip install -e .
5.  pip install bin/intersystems_irispython-3.2.0-py3-none-any.whl
6.  install sqlite3


## Usage
__Setup environment__
1. Generate a json config file. This also generates a .env file that points to this config files location
   1. python scripts/generate_configs.py
2. Create a /tmp/iceberg directory, or change the locations in the config for local files
3. Load data into sqlite
   1. sqlite3 /tmp/iceberg/test.db < data/devdata.sql 

__Basic commands__
1. irice --job_type="list_tables"
   1. Lists all of the tables in the Catalog 
2. 

## Configurations


## Notes
  - sqlalchemy-iris==0.12.0 is required, later versions convert timestamps to strings   
