import os
import json 
import sys 

from dotenv import load_dotenv

load_dotenv()

base = {
    "job_type": "list_tables",
    "table_chunksize": 100,
    "sql_clause": "",
    "source_table_name": "iris_demo.titanic",
    "target_table_name": "iris_demo.titanic",
    "partition_field": "PassengerID",
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
            "password": "SYS",
            "user": "_system",
            "port": 1972,
            "schemas": ["iris_demo",],
            "connection_type": "db-api",
        }
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
            "uri": "iris://_SYSTEM:sys@localhost:5551/USER",
            "adls.connection-string": os.environ.get("adls.CONNECTION_STRING"),
            "adls.account-name": "",
            "location": "abfs://??",
        },
    ] 
}

local_testing_config = {
    "src_server": "LocalTesting",
    "target_iceberg": "LocalTesting",
}

local_testing_config.update(base)

if __name__ == "__main__":

    current_dir = os.getcwd()
    config_path = os.path.join(current_dir, 'local_testing_config.json')
     
    # Generates a json config for any dictionary defined that ends with _config
    json.dump(local_testing_config, open(config_path, "w"), indent=2)
    with open('.env', "w") as fo:
        fo.writelines(f'IRISICE_CONFIG_PATH="{config_path}"')
