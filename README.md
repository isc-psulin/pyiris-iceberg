# IRIS-ICEBERG
The iris-iceberg library provides utilities for replicating IRIS(SQL) tables into Iceberg tables. It uses the pyiceberg, https://py.iceberg.apache.org/, library to interact with iceberg tables.

This project is meant as an exploration of Iceberg and the PyIceberg library. The primary goal of this exploration is to test replicating IRIS tables into Iceberg tables. The easiest way to test the library is to use the CLI


## Installation
1. git clone git@github.com:isc-patrick/iris-iceberg.git
2. cd iris-iceberg
3. Create and activate a virtualenv
4. Get The iris DB-API library, https://intersystems-community.github.io/iris-driver-distribution/ and install it
5. X pip install -r requirements.txt
6. pip install -e .
7. Add a .env file to the project root with a adls.CONNECTION_STRING (this is only needed for writing to Azure)
8. Create a /tmp/iceberg directory, or change the locations in the config for local files

## Usage
1. Generate a json config file: 
   1. python scripts/generate_configs.py
2. Load data into sqlite
   1. sqlite3 /tmp/iceberg/test.db < data/devdata.sql 

## Configurations


## Notes
  - sqlalchemy-iris==0.12.0 is required, later versions convert timestamps to strings   
