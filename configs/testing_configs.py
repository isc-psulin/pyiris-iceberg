import os

from dotenv import load_dotenv
load_dotenv()

base = {
    "servers": [
        {
            "name": "LocalTesting",
            "dialect": "sqlite",
            "database": "/Users/psulin/projects/insights/python/insights/tests/data/test.db",
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
            "schemas": ["FS", "SQLUSER"],
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
            "uri": "",
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

local_testing.update(base)
iris_src_local_target.update(base)