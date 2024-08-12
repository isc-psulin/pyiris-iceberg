import os

from dotenv import load_dotenv
load_dotenv()

base = {
    "servers": [
        {
            "name": "LocalTesting",
            "dialect": "sqlite",
            "database": "/tmp/iceberg/test.db",
            "warehouse": "/tmp/iceberg",
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
            "field_exclusions": {"table_name": "FS.SecurityMaster", "fields": ["composite_figi"]}
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
            "uri": "sqlite:////tmp/iceberg/pyiceberg_catalog.db",
            "adlfs.connection-string": os.environ["ADLFS.CONNECTION_STRING"],
            "adlfs.account-name": "testiris",
            "type": "azure",
            "py-io-impl": "pyiceberg.io.fsspec.FsspecFileIO",
            "database": "testiris",
            "location": "abfs://mgb"
        }
        ]
}

local_testing = {
    "src_server": "LocalTesting",
    "target_iceberg": "LocalTesting"
}

iris_src_local_target = {
    "src_server": "LocalIRIS",
    "target_iceberg": "LocalTesting"
}

local_src_azure_target = {
    "src_server": "LocalIRIS",
    "target_iceberg": "Azure"
}

local_testing.update(base)
iris_src_local_target.update(base)
local_src_azure_target.update(base)
