# IRIS-ICEBERG
The iris-iceberg library provides utilities for replicating IRIS(SQL) tables into Iceberg tables. It uses the pyiceberg, https://py.iceberg.apache.org/, library to interact with iceberg tables.

This project is meant as an exploration of Iceberg and the PyIceberg library and replicating IRIS tables into Iceberg tables.
This can be installed via docker with an IRIS instance and tested through the terminal or just via Python. In both cases, the commands are driven primarily through a configuration file, in this case named local_testing_config.json.


## IRIS Docker Installation and basic use
1. git clone git@github.com:isc-patrick/pyiris-iceberg.git
2. cd pyiris-iceberg
3. docker compose build
4. docker compose up -d
5. docker exec -it pyiris-iceberg-iris-1 /bin/bash
6. ./install.sh
7. iris session iris
8. zn "IRISAPP"
9. Check the install by listing the iceberg tables
      - do ##class(User.iceberg).ListTables()
10. Move the data from the iceberg_demo.titanic table to an iceberg table on your local file system
    -  do ##class(User.iceberg).InitialTableSync()
11. View the data in the iceberg table
    -  do ##class(User.iceberg).SelectAll()
12. View the data files for the iceberg table
    -  !find /tmp/iceberg/iceberg_demo.db  
13. Delete the iceberg table
    -  do ##class(User.iceberg).PurgeTable()

## Python Only Installation
1. git clone git@github.com:isc-patrick/pyiris-iceberg.git
2. cd pyiris-iceberg
3. Create and activate a virtualenv
4. pip install .
5. pip install bin/intersystems_irispython-3.2.0-py3-none-any.whl
6. install sqlite3

__Setup environment__  
1. Generate a json config file. This also generates a .env file that points to this config files location
   1. python scripts/generate_configs.py
2. Create a /tmp/iceberg directory, or change the locations in the config for local files
3. Load data into sqlite
   1. sqlite3 /tmp/iceberg/test.db < data/devdata.sql 

__CLI command list__  
There are just a few commands using the CLI, irice
   * irice --job_type=list_tables
       - Lists all the tables in the Iceberg catalog
   * irice --job_type=initial_table_sync
      - Uses a source table to create an Iceberg table, using the schema data from the source table, and copies the data from the source table into the target Iceberg table. The values for these are all in the config file with easy to understand names like source_tablename, target_tablename, etc. This will also create the Iceberg catalog tables if necessary.
   * irice --job_type=update_table
      - This copies the data form a source table to a target table, but does not create the Iceberg table or create the Iceberg catalog tables
   * irice --job_type=purge-table
      - Deletes the Iceberg table from the catalog and the metadata and data files

__Simple walkthrough of commands with Python install__  
In the environment setup, you added data to a source table and created a config file that you be used for initial. Follow these steps to walk through the basic commands
1. irice --job_type=list_tables
   1. Lists all of the tables in the Catalog 
2. irice --job_type=initial_table_sync
   1. Copies data from test db into Iceberg tables
   2. Run this to see the Iceberg metadata and data files
      1. find /tmp/iceberg/DevStats.db/
   3. Run the list tables command again  
3. irice --job_type=update_table
   1. Run the find command and you will see the data has all been compied over again. 
4. irice --job_type=purge_table
5. Run the find command again and you will see that the data files has been removed

## Configurations

## Notes
  - sqlalchemy-iris==0.12.0 is required, later versions convert timestamps to strings  


