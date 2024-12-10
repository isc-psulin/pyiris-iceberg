import os

from dotenv import load_dotenv
load_dotenv()

base = {
    "table_chunksize": 50000,
    "sql_clause": "",
    "table_name": "",
    "partition_field": "ID",
    "servers": [
        {
            "name": "LocalTesting",
            "dialect": "sqlite",
            "database": ":memory:",
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
            "schemas": [],
            "connection_type": "db-api"
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
            "adls.connection-string": os.environ.get("adls.CONNECTION_STRING"),
            "adls.account-name": "",
            "location": "abfs://"
        }
        ]
}


iris_src_local_target = {
    "src_server": "LocalIRIS",
    "target_iceberg": "LocalTesting"
}


iris_src_local_target.update(base)
