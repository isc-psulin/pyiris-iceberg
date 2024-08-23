# IRIS-ICEBERG
The iris-iceberg library provides utilities for replicating IRIS(SQL) tables into Iceberg tables. It uses the pyiceberg, https://py.iceberg.apache.org/, library to interact with iceberg tables.

This project is meant as an exploration of Iceberg and the PyIceberg library. The primary ggoal of this exploration is to test replicating IRIS tables into Iceberg tables, identify the requirements for a production ready library while serving as a starting point for that library and not just a POC or prototype. This includes understanding the scope of the features PyIceberg, what needs to be provided on top of these features, generally learning more about Iceberg and the Iceberg ecosystem, and doing this within an application framework that can be continously extended and used in a production environment.

    - Configuration driven
        - Allows for reliable, rapid testing against local and remote sources
        - Provides a record of what exactly what was executed
    - Job based execution
      - A job is a unit of work that needs to be clearly defined, composed of discreet and atomic steps that can be verified and replayed if necessarty

## Features

Below is a list of the Operational Feature, which are classified as either Data Jobs or Admin tasks. Data jobs usually involve reading, writing large amounts of data or deleting data. Every job and every step in the job is recorded as a permanent record of action taken on any data and includes start and end time, record IDs, status, and erros. Admin tasks are used for summary information.

    1. Data Jobs
       1. [x] Initial table sync: Replicates an IRIS table into an iceberg table
          1. [x] Dynamically determines schema an automatically creates iceberg table
          2. [x] Takes any valid SQL conditions to limit the scope of the data transfer
       2. [x] Update table: Updates an existing iceberg table with data from the IRIS source table
          1. [x] Takes any set of valid SQL conditions to limit the scope of the data transfer
       3. [x] Purge table: Delete an iceberg table and all data
    2. Admin tasks
       1. [X] List all the Jobs and Job steps
       2. [ ] List all tables in the iceberg catalog
   

## Installation
1. git clone git@github.com:isc-patrick/iris-iceberg.git
2. cd iris-iceberg
3. Create and activate a virtualenv
4. Get The iris DB-API library, https://intersystems-community.github.io/iris-driver-distribution/
5. pip install -r requirements.txt
6. pip install -e .
7. Add a .env file to the project root with a ADLFS.CONNECTION_STRING (this is only needed for writing to Azure)
8. Create a /tmp/iceberg directory, or change the locations in the config for local files

## Installation Notes
    - This library uses an editable install and absolute imports


## Other things to know about the code
- Data replication and updates does not rely on predefining schemas. Schema is dynamically loaded from IRIS when table is created in Iceberg.
      - Any clause can be provided to limit the scope of the data transfer
        - For initial_table_sync this would typically be a max timestamp or id
        - For table_updates this clause will be created by another process that uses admin records of table transfers to determine next segment

# TODO
 1. Features
    1. Add the option to use predefined schemas for IRIS src, pandas, and arrow
    2. Validate table data: Validate data in iceberg table against data in IRIS table
          1. Takes any valid SQL conditions and compares each record in the SRC table against the iceberg table
          2. Returns a list of records that do not match
    3. Add multiprocessing
 2. Refactoring
    1. Extract the Database session as a separate class
    2. Remove loging instantiation from IRIS class
 3. Testing
    1. Test all datatype mapping - Create an IRIS class with every possible datatype


## What we learned
    1. Data validation outside of data types is the responsibility of the iceberg engine
       1. Iceberg tables are simple compared to SQL tables: There are no indices, keys, or constraints.
       2. This means a lot more admin level features need to be put in place to validate that EXACTLY all of the data has been replicated as expected
       3. Some Iceberg engines provide features that are not part of the Iceberg spec, like Unique field constraints
          1. The assumption is that there must be some other data being stored to record the equivilant of a unique index. Otherwise, a full table scan would be required before any writes.
    2. Write semantics of any specific engine are not a 1-1 mapping to Iceberg spec. A good understanding of Iceberg is necessary, but even then exact mapping of an engine's API the the write semantics of Iceberg is not clear.
    3. Tech details
       1. Using ODBC via pyodbc to load into pandas is 50-60 times faster than using the ISC DB-API
       2. 


## Next explorations
    1. Pass-thorugh queries for reading from Iceberg from IRIS
       1. https://docs.intersystems.com/irislatest/csp/docbook/DocBook.UI.Page.cls?KEY=GSQL_foreigntables
    2. Foreign tables
       1. https://openexchange.intersystems.com/package/IRIS-External-Table-Driver
   

## Notes
  - sqlalchemy-iris==0.12.0 is required, later versions convert timestamps to strings   