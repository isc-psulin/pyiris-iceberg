# IRIS-ICEBERG
The iris-iceberg library provides utilities for replicating IRIS(SQL) tables into Iceberg tables. It uses the pyiceberg, https://py.iceberg.apache.org/, library to interact with iceberg tables.

## Features

    1. Replicate an IRIS table into an iceberg table
    2. Keep a replicated Iceberg IRIS table in synch with source IRIS table


## Installation

1. git clone git@github.com:isc-patrick/iris-iceberg.git
2. cd iris-iceberg
3. Create and activate a virtualenv
4. pip install -e .


## Installation Notes
    - This library uses an editable install and absolute imports
