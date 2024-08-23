import os

from dotenv import load_dotenv

load_dotenv()

base = {
    "table_chunksize": 50000,
    "sql_clause": "",
    "table_name": "FS.AccountPosition2",
    "partition_field": "ID",
    "servers": [
        {
            "name": "LocalTesting",
            "dialect": "sqlite",
            "database": "/tmp/iceberg/test.db",
            "warehouse": "/tmp/iceberg",
            "connection_type": "sqlite",
            "schemas": [],
        },
        {
            "name": "LocalIRIS",
            "dialect": "iris",
            "database": "User",
            "driver": "com.intersystems.jdbc.IRISDriver",
            "host": "localhost",
            "password": "sys",
            "user": "_system",
            "port": 1972,
            "schemas": ["FS"],
            "connection_type": "db-api",
        },
        {
            "name": "AzureIRIS",
            "dialect": "iris",
            "database": "DevStats",
            "driver": "com.intersystems.jdbc.IRISDriver",
            "host": "48.217.241.83",
            "password": "iris-iceberg",
            "user": "azureuser",
            "port": 1972,
            "schemas": ["DevStats"],
            "connection_type": "db-api",
        },
    ],
    "icebergs": [
        {
            "name": "LocalTesting",
            "uri": "sqlite:////tmp/iceberg/pyiceberg_catalog.db",
            "warehouse": "/tmp/iceberg",
            "type": "sqlite",
        },
        {
            "name": "Azure",
            "uri": "iris://_SYSTEM:sys@localhost:1972/USER",
            "adlfs.connection-string": os.environ["ADLFS.CONNECTION_STRING"],
            "adlfs.account-name": "testiris",
            "location": "abfs://mgb",
        },
    ],
}

local_testing = {
    "src_server": "LocalTesting",
    "admin_server": "LocalTesting",
    "catalog_server": "LocalTesting",
    "target_iceberg": "LocalTesting",
}

iris_src_local_target = {
    "src_server": "LocalIRIS",
    "admin_server": "LocalIRIS",
    "catalog_server": "LocalTesting",
    "target_iceberg": "LocalTesting",
}

iris_src_azure_target = {
    "src_server": "LocalIRIS",
    "admin_server": "LocalIRIS",
    "catalog_server": "LocalIRIS",
    "target_iceberg": "Azure",
}

azure_src_local_target = {
    "src_server": "AzureIRIS",
    "admin_server": "AzureIRIS",
    "catalog_server": "AzureIRIS",
    "target_iceberg": "LocalTesting",
}


local_testing.update(base)
iris_src_local_target.update(base)
iris_src_azure_target.update(base)
azure_src_local_target.update(base)
