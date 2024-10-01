import os
import json 
import sys 

from dotenv import load_dotenv

load_dotenv()

base = {
    "job_type": "list_tables",
    "table_chunksize": 100000,
    "sql_clause": "id < 300001",
    "table_name": "FS.AccountPosition2",
    "partition_field": "ID",
    "grid_type": "tabulator",
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
            "port": 5551,
            "schemas": ["SQLUSER",],
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
            "name": "IRISCatalogLocalWarehouse",
            "uri": "iris://_SYSTEM:sys@localhost:5551/USER",
            "warehouse": "/tmp/iceberg",
            "type": "sqlite",
        },
        {
            "name": "Azure",
            "uri": "iris://azureuser:iris-iceberg@48.217.241.83:1972/DevStats",
            "adls.connection-string": os.environ["adls.CONNECTION_STRING"],
            "adls.account-name": "testiris",
            "location": "abfs://iceberg",
        },
        {
        "name": "PatAzure",
        "uri": "iris://_SYSTEM:sys@localhost:5551/USER",
        "adls.connection-string": os.environ["adls.CONNECTION_STRING"],
        "adls.account-name": "testiris",
        "location": "abfs://mgb",
        },
    ],
    "catalogs": [
            {"name": "SQLite",
            "uri": "sqlite:////tmp/iceberg/pyiceberg_catalog.db",
            "type": "sql"},
            {"name": "IRISLocal",
            "uri": "iris://_SYSTEM:sys@localhost:5551/USER",
            "type": "sql"}
    ],
    "warehouses": [
         {
            "name": "Local",
            "warehouse": "/tmp/iceberg"
        },
         {
            "name": "Azure1",
            "adls.connection-string": os.environ["adls.CONNECTION_STRING"],
            "adls.account-name": "testiris",
            "location": "abfs://iceberg",
        },
    ]
}

# No local data yet 
local_testing_config = {
    "src_server": "LocalTesting",
    "admin_server": "LocalTesting",
    "catalog_server": "LocalTesting",
    "target_iceberg": "LocalTesting",
}

iris_src_local_target_config = {
    "src_server": "LocalIRIS",
    "job_server": "LocalIRIS",
    "catalog_server": "LocalIRIS",
    "target_iceberg": "IRISCatalogLocalWarehouse",
}

iris_src_azure_target_config = {
    "src_server": "LocalIRIS",
    "admin_server": "LocalIRIS",
    "catalog_server": "LocalIRIS",
    "target_iceberg": "Azure",
}

azure_src_local_target_config = {
    "src_server": "AzureIRIS",
    "admin_server": "AzureIRIS",
    "catalog_server": "AzureIRIS",
    "target_iceberg": "LocalTesting",
}

local_iris_src_azurepat_target_config = {
    "src_server": "LocalIRIS",
    "admin_server": "LocalIRIS",
    "catalog_server": "LocalIRIS",
    "target_iceberg": "PatAzure",
}

local_testing_config.update(base)
iris_src_local_target_config.update(base)
iris_src_azure_target_config.update(base)
azure_src_local_target_config.update(base)
local_iris_src_azurepat_target_config.update(base)

if __name__ == "__main__":
    
    if len(sys.argv) == 2:
    
        if sys.argv[1] == "gen":
            configs = [k for k,v in locals().items() if k.endswith("_config")]
            for c in configs:
                json.dump(locals()[c], open(f'./configs/{c}' + ".json", "w"), indent=2)
