# IRIS-ICEBERG
The iris-iceberg library provides utilities for replicating IRIS(SQL) tables into Iceberg tables. It uses the pyiceberg, https://py.iceberg.apache.org/, library to interact with iceberg tables.

This project is meant as an exploration of Iceberg and the PyIceberg library and replicating IRIS tables into Iceberg tables. This can be installed via docker with an IRIS instance and tested in an IRIS terminal or just via Python. In both cases, the commands are driven primarily through a configuration file, in this case named local_testing_config.json.


## IRIS Docker installation and basic use
```bash
# Get the code, build run the docker container
git clone git@github.com:isc-patrick/pyiris-iceberg.git
cd pyiris-iceberg
docker compose build
docker compose up -d

# Connect to the container to complete installation
docker exec -it pyiris-iceberg-iris-1 /bin/bash
./install.sh

# Test some commands from the terminal
iris session iris
zn "IRISAPP"

# This will list all the Iceberg tables, so you shold see an empty list
do ##class(User.iceberg).ListTables()  

# This will use an IRIS table to create a corresponding Iceberg table and copy data to the new table
do ##class(User.iceberg).UpdateTable()  

# This use the pyiceberg scan() method to show the data
do ##class(User.iceberg).SelectAll()

# 
irice --job_type=update_table --src_server "LocalTesting"

# List the files created for the Iceberg table
!find /tmp/iceberg/iceberg_demo.db  
do ##class(User.iceberg).PurgeTable()
```

## Python Only Installation
1. git clone git@github.com:isc-patrick/pyiris-iceberg.git
2. cd pyiris-iceberg
3. Create and activate a virtualenv
4. pip install .
5. pip install bin/intersystems_irispython-3.2.0-py3-none-any.whl
6. install sqlite3

__Setup environment__  
1. Create a /tmp/iceberg directory, or change the location in the config for local files
2. Load data into sqlite
   1. sqlite3 /tmp/iceberg/test.db < data/titanic.sql 

__CLI command examples__  
There are just a few commands using the CLI, irice - list_tables, initial_table_sync, update_table, purge_table

```bash
# Lists all the tables in the Iceberg catalog
irice --job_type=list_tables --src_server "LocalTesting"

# Uses a source table to create an Iceberg table, using the schema data from the source table, and copies 
# the data from the source table into the target Iceberg table. The values for these are all in the config file with # easy to understand names like source_tablename, target_tablename, etc. This will also create the Iceberg catalog 
# tables if necessary.
irice --job_type=initial_table_sync --src_server "LocalTesting"

# View the files created for the Iceberg table
find /tmp/iceberg/iceberg_demo.db  

# This copies the data form a source table to a target table, but does not create the Iceberg table or create the Iceberg catalog tables     
irice --job_type=update_table --src_server "LocalTesting"

# Deletes the Iceberg table from the catalog and the metadata and data files
irice --job_type=purge-table --src_server "LocalTesting"
```