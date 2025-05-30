# IRIS-ICEBERG
The iris-iceberg library provides utilities for replicating IRIS(SQL) tables into Iceberg tables. It uses the pyiceberg, https://py.iceberg.apache.org/, library to interact with iceberg tables.

This project is meant as an exploration of Iceberg and the PyIceberg library and replicating IRIS tables into Iceberg tables. This can be installed via docker with an IRIS instance and tested in an IRIS terminal or just via Python. In both cases, the commands are driven primarily through a configuration file, in this case named local_testing_config.json.  

There are just 4 commands/methods
1. list_tables: List all of the Iceberg tables
2. initial_table_sync: Creates an Iceberg table, deleting a table if it already exists from an IRIS source table and copies data into the Iceberg table
3. update_table: Same as initial_table_sync but it only works with existing Iceberg tables
4. purge_table: Deletes an Iceberg table and its data

## Docker installation and basic use
1. Clone this repo, https://github.com/isc-patrick/pyiris-iceberg
```bash
docker build --tag iris-ice pyiris-iceberg/.
docker compose -f pyiris-iceberg/docker-compose.yml up -d
#docker run  --name iris-ice -p 1972:1972 -p 52773:52773 -v ./:/home/irisowner/dev -v ./tmp:/tmp -d iris-ice

docker exec -it iris-ice /bin/bash

pip install .

irice --help
```

Now, you can invoke either directly from the CLI in the container or in an IRIS session.

For use from the CLI, use these [steps](#cli-examples). 

From an IRIS Session:
```bash
# Test some commands from the terminal
iris session iris
zn "IRISAPP"

# This will list all the Iceberg tables, so you shold see an empty list
do ##class(User.iceberg).ListTables()  

# This will use an IRIS table to create a corresponding Iceberg table and copy data to the new table
do ##class(User.iceberg).InitialTableSync()  

# This use the pyiceberg scan() method to show the data
do ##class(User.iceberg).SelectAll()

# Update an existing ICeberg table with data from the IRIS source table
do ##class(User.iceberg).UpdateTable()  

# List the files created for the Iceberg table
!find /home/irisowner/dev/iceberg_data/iceberg_demo.db  
do ##class(User.iceberg).PurgeTable()
```

## Python Only Installation
1. Clone this repo
2. cd pyiris-iceberg
3. Create and activate a virtualenv
4. pip install .
5. pip install bin/intersystems_irispython-3.2.0-py3-none-any.whl
6. install sqlite3

__Setup environment__  
1. Load data into sqlite
   1. sqlite3 /home/irisowner/dev/iceberg_data/test.db < data/titanic.sql 

## <a id="cli-examples">CLI command examples</a>

If you are using these from the docker install, remove the --src_server arg
```bash
# Lists all the tables in the Iceberg catalog
irice --job_type=list_tables --src_server "LocalTesting"

# Uses a source table to create an Iceberg table, using the schema data from the source table, and copies 
# the data from the source table into the target Iceberg table. The values for these are all in the config file with 
# easy to understand names like source_tablename, target_tablename, etc. This will also create the Iceberg catalog 
# tables if necessary.
irice --job_type=initial_table_sync --src_server "LocalTesting"

# View the files created for the Iceberg table
find /home/irisowner/dev/iceberg_data/iceberg_demo.db  

# This copies the data forfromm a source table to a target table, but does not create the Iceberg table or create the Iceberg catalog tables     
irice --job_type=update_table --src_server "LocalTesting"

# Deletes the Iceberg table from the catalog and the metadata and data files
irice --job_type=purge_table --src_server "LocalTesting"
```
