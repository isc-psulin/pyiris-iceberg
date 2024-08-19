
from pydantic import BaseModel
from pydantic import ConfigDict
from typing import Optional, List
import iris
from sqlalchemy import MetaData, create_engine, Table, Column, Integer, String, Float, inspect
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField
import pytest
import pandas as pd

config1 = {
    "servers": [
        {
            "name": "test",
            "dialect": "sqlite",
            "database": "/Users/psulin/projects/insights/python/insights/tests/data/test.db",
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
    "src_server": "LocalIRIS",
     "icebergs": [
        {
            "name": "Test",
            "uri": "sqlite:////tmp/iceberg/pyiceberg_catalog.db",
            "warehouse": "/tmp/iceberg",
            "type": "sqlite",
        },
        {
            "name": "Azure",
            "uri": "",
            "adlfs.connection-string": "DefaultEndpointsProtocol=https;AccountName=testiris;AccountKey=g+wwoh1ohZaPrLN+tb+Ed8RE+T4y5au60aptelCbpbIy48v3G1q1biT0MBOgkMSWY6SJFpssi2o8+ASt0hqftQ==;EndpointSuffix=core.windows.net",
             "adlfs.account-name": "testiris",
             "type": "azure",
            "py-io-impl": "pyiceberg.io.fsspec.FsspecFileIO",
            "database": "testiris",
            "location": "abfs://mgb"
        }
        ],
        "target_iceberg": "Test"
}

# Pydantic models are used to validate configurations before code is executed
class MyBaseModel(BaseModel):
   # This allows there to be extra fields
   model_config = ConfigDict(extra='allow', populate_by_name=True)

class IRIS_Config(MyBaseModel): 
    name: str
    database: str
    dialect: str
    driver: Optional[str] = None
    host: Optional[str] = ""
    password: Optional[str] = None
    user: Optional[str] = None
    port: Optional[int] = None
    schemas: Optional[list[str]] = []

class Iceberg_Config(MyBaseModel): 
    name: str
    uri: Optional[str] = ""

class Configuration(MyBaseModel):
    servers: Optional[List[IRIS_Config]] = []
    icebergs: Optional[List[Iceberg_Config]] = []
    src_server: Optional[str] = None

def get_alchemy_engine(config: Configuration):  
    
    server = get_from_list(config.servers, config.src_server)
    
    connection_url = create_connection_url(server)
    engine = create_engine(connection_url)
 
    return engine

def create_connection_url(server: IRIS_Config):
     
     # Create a connection url from the server properties in this form dialect+driver://username:password@host:port/database
     # Only adding sections if they have a value in the server instance
     
     # sqlite requires 3 slashes for reference to file db
     seperator = ":///" if server.dialect == "sqlite" else "://"
     driver_dialect = f"{server.dialect}{seperator}" #if not server.driver else f"{server.dialect}+{server.driver}{seperator}"
     user_pass = f"{server.user}:{server.password}@" if server.user and server.password else ""
     host_port = f"{server.host}:{server.port}/" if server.host and server.port else ""
     database = f"{server.database}"
     
     return driver_dialect+user_pass+host_port+database

def get_from_list(lyst: str, name: str) -> MyBaseModel: 
    for item in lyst:
        if item.name == name:
            return item
    return None

def sqlalchemy_to_iceberg_schema(table: Table) -> Schema:
    """
    Convert an SQLAlchemy Table schema to an Iceberg Schema.
    
    :param table: SQLAlchemy Table object
    :return: Iceberg Schema object
    """
    from pyiceberg.types import (
        BooleanType,
        IntegerType,
        LongType,
        FloatType,
        DoubleType,
        DateType,
        TimestampType,
        StringType,
    )
    from sqlalchemy import Integer, BigInteger, Float, Boolean, Date, DateTime, String, Text, BIGINT

    type_mapping = {
        Integer: IntegerType(),
        BigInteger: LongType(),
        Float: FloatType(),
        Boolean: BooleanType(),
        Date: DateType(),
        DateTime: TimestampType(),
        String: StringType(),
        Text: StringType(),
        BIGINT: LongType(),
    }

    iceberg_fields = []
    for i, column in enumerate(table.columns, start=1):
        iceberg_type = type_mapping.get(type(column.type), StringType())
        iceberg_fields.append(NestedField(
            field_id=i,
            name=column.name,
            field_type=iceberg_type,
           # required=not column.nullable
        ))

    return Schema(*iceberg_fields)

def read_sql_with_dtypes(engine, table_name):
 
    # Parse schema and table name
    if '.' in table_name:
        schema, table = table_name.split('.', 1)
    else:
        schema, table = None, table_name
    
    # Get table metadata
    inspector = inspect(engine)
    columns = inspector.get_columns(table, schema=schema)
    
    # Create a dictionary to map SQL types to pandas dtypes
    dtype_map = {
        'INTEGER': 'int64',
        'BIGINT': 'int64',
        'SMALLINT': 'int32',
        'FLOAT': 'float64',
        'REAL': 'float32',
        'DOUBLE': 'float64',
        'NUMERIC': 'float64',
        'DECIMAL': 'float64',
        'CHAR': 'string',
        'VARCHAR': 'string',
        'TEXT': 'string',
        'DATE': 'datetime64[ns]',
        'TIMESTAMP': 'datetime64[ns]',
        'BOOLEAN': 'bool',
        'TINYINT': 'string'
    }
    
    # Create a dictionary of column names and their corresponding pandas dtypes
    dtypes = {col['name']: dtype_map.get(str(col['type']).split('(')[0].upper(), 'object') 
              for col in columns}
    
    # Construct the full table name for the query
    full_table_name = f"{schema+'.' if schema else ''}{table}"
    
    # Read the SQL table into a DataFrame with specified dtypes
    # TODO - MOve chunkSize to config
    query = f"SELECT * FROM {full_table_name}"
    for df in pd.read_sql(query, engine, dtype=dtypes, chunksize=5000):

        # Convert date and timestamp columns
        for col in columns:
            if str(col['type']).upper().startswith(('DATE', 'TIMESTAMP')):
                df[col['name']] = pd.to_datetime(df[col['name']])
        
        yield df

    