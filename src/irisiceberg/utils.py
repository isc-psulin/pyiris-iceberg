import math 
import sys
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

from typing import Iterable, Optional, List

import iris

from sqlalchemy import MetaData, create_engine, Table, Column, Integer, String, Float, inspect, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField
import pytest
import pandas as pd
from loguru import logger
from sqlalchemy.orm import declarative_base
import logging
from datetime import datetime

# Create a Base class for declarative models
Base = declarative_base()

# Create a dictionary to map SQL types to pandas dtypes
sql_to_pandas_typemap = {
        'INTEGER': 'int32',
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

class IterableWrapper(Iterable):
    """ Simple wrapping class for an iterator and a set of attribute

    Args:
        iterator (Iterable): iterator to wrap
        attributes (dict): dictionary of attributes to return with each iteration
    """
    def __init__(self, iterator: Iterable, attributes: dict = {}) -> None:
        self.iterator = iterator
        self.attributes = attributes
            
    def __iter__(self):
        for i in self.iterator:
            yield (i, self.attributes,)
            
    def append(self, obj: object, attributes: dict) -> None:
        self.iterator.append((obj, attributes,))

# Pydantic models are used to validate configurations before code is executed
class MyBaseModel(BaseSettings):
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
     if server.connection_type in ['sqlite', 'db-api']:
         url = get_generic_connection_url(server)
         return url
     
def get_generic_connection_url(server: IRIS_Config):
    
     seperator = ":///" if server.dialect == "sqlite" else "://"
     driver_dialect = f"{server.dialect}{seperator}" #if not server.driver else f"{server.dialect}+{server.driver}{seperator}"
     user_pass = f"{server.user}:{server.password}@" if server.user and server.password else ""
     host_port = f"{server.host}:{server.port}/" if server.host and server.port else ""
     database = f"{server.database}"
     
     return driver_dialect+user_pass+host_port+database

def get_odbc_connection(server: IRIS_Config):
    
    # Added here to prevent loading if not ever using odbc
    import pyodbc

    con_str = 'DRIVER={Default};SERVER='+server.host+';PORT='+str(server.port)+';DATABASE='+server.database+';UID='+server.user+';PWD='+ server.password

    cnxn = pyodbc.connect(con_str)
    cnxn.setdecoding(pyodbc.SQL_CHAR, encoding='latin1')
    cnxn.setencoding(encoding='utf-8', ctype=pyodbc.SQL_CHAR)

    return cnxn, con_str

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
    from sqlalchemy import INTEGER, BIGINT, FLOAT, BOOLEAN, DATE, DATETIME, String, TEXT, TIMESTAMP
    from sqlalchemy_iris import DOUBLE

    type_mapping = {
        INTEGER: IntegerType(),
        BIGINT: LongType(),
        FLOAT: FloatType(),
        BOOLEAN: BooleanType(),
        DATE: TimestampType(), #DateType(),
        DATETIME: TimestampType(),
        String: StringType(),
        TEXT: StringType(),
        DOUBLE: DoubleType(),
        TIMESTAMP: TimestampType()
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

def load_data_type_map(tablename, engine):
    
    if '.' in tablename:
        schema, table = tablename.split('.', 1)
    else:
        schema, table = None, tablename

    inspector = inspect(engine)
    columns = inspector.get_columns(table, schema=schema)
    
    # Create a dictionary of column names and their corresponding pandas dtypes
    dtypes = {col['name']: sql_to_pandas_typemap.get(str(col['type']).split('(')[0].upper(), 'object') 
              for col in columns}
    
    return columns, dtypes

def read_sql_to_df(connection, table_name, clause: str = '', chunksize: int = 5000, metadata: MetaData = None):
    
    columns = metadata.tables.get(table_name).columns

    dtypes = {col.name: sql_to_pandas_typemap.get(str(col.type).split('(')[0].upper(), 'object') 
              for col in columns}
    
    where = f"WHERE {clause}" if clause else ''
    query = f"SELECT * FROM {table_name} {where}"
    logger.debug(f"Query: {query}")
    
    for df in pd.read_sql(query, connection, dtype=dtypes, chunksize=chunksize):
        for col in columns:
            if str(col.type).upper().startswith(('DATE', 'TIMESTAMP')):
                df[col.name] = pd.to_datetime(df[col.name])
        
        yield df

def split_sql(tablename, min_id, max_id, partition_size, row_count, clause):
        """ Generate SQL SELECT statements of equal partitions of records function
        """
        part_size = gap_fill_partition(min_id, max_id, partition_size, row_count)
        logger.info(f"New Part size {part_size}")
        sql_partitions = generate_select_queries(min_id=min_id, max_id=max_id, 
                                                partition_size=part_size,
                                                tablename=tablename, clause=clause) # -> base.IterableWrapper

        logger.info(f"Generated {len(sql_partitions.iterator)} SQL queries")
        return sql_partitions

def gap_fill_partition(min_id, max_id, partition_size, row_count):
    """ Adjust the partition size to accomodate for sparsity in the parittion key values"""
    fullrange = max_id - min_id
    sparsity = fullrange - row_count
    if sparsity < 1000:
        return partition_size
    multiple = math.ceil(fullrange/row_count)
    new_part = partition_size * multiple
    logger.debug(f"New partition size {new_part}")
    return new_part

def generate_select_queries(min_id: int, max_id: int, partition_size:int, tablename : str,
                            fields:list = [], clause:str = ""):
    """ A function that takes a min id, max id, partition size, table name, list of fields and list of clauses 
    and generates a list of SQL queries selecting all records from a table, where each query selects one parition
    
    Args:
        min_id (int): _description_
        max_id (int): _description_
        partition_size (int): _description_
        table_name (str): _description_
        fields (list): _description_
        clauses (list): _description_
    """
    #queries = []
    logger.info(f"generate_select_queries: min_id = {min_id}, max_id = {max_id}")
    queries_obj = IterableWrapper([])
    
    # Set the intitial min and max ids
    query_max_id = partition_size
    query_min_id = 0
    i=0
    
    # When the query min id is > than the max_id, then all partitions are complete
    while query_min_id < max_id:  
        query = "SELECT "
        if not fields:
            query += " * "
        else:
            fields = []
            for field in fields:
                fields.append(field)
                
            query += ", ".join(fields)
        
        
        query += " FROM " + tablename + " WHERE id >= " + str(query_min_id) + \
                 " AND id < " + str(query_max_id)
        
        if clause:
            query = " AND " + clause
        
        queries_obj.append(query, {"table": tablename, "min_id": query_min_id, "max_id": query_max_id})
        
        # Update counters for next ierations 
        query_min_id = (min_id + i) * partition_size
        query_max_id = (min_id + i + 1) * partition_size
        i += 1
   
    return queries_obj

def downcast_timestamps(df):
        # Convert all datetime64[ns] columns to datetime64[us]
        for column in df.select_dtypes(include=['datetime64[ns]']).columns:
            df[column] = df[column].astype('datetime64[us]')
        return df

Base = declarative_base()

class IceBergJobs(Base):
    __tablename__ = 'iceberg_jobs'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    job_name = Column(String(100))
    action_name = Column(String(100))
    tablename = Column(String(100))
    catalog_name = Column(String(100))
    src_min_id = Column(BigInteger)
    src_max_id = Column(BigInteger)
    src_timestamp = Column(DateTime)

def create_iceberg_jobs_table(engine):
    Base.metadata.create_all(engine)

class LogEntry(Base):
    __tablename__ = "log_entries"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    level = Column(String)
    message = Column(String)
    module = Column(String)
    function = Column(String)
    line = Column(Integer)

class SQLAlchemyLogHandler:
    def __init__(self, engine):
        self.engine = engine

    def write(self, message):
        record = message.record
        log_entry = LogEntry(
            level=record["level"].name,
            message=record["message"],
            module=record["module"],
            function=record["function"],
            line=record["line"]
        )
        with self.engine.connect() as conn:
            conn.execute(LogEntry.__table__.insert().values(log_entry.__dict__))
            conn.commit()

# Global logger instance
logger.remove()  # Remove default handler
logger.add(sys.stderr, level="DEBUG")  # Add console handler

def get_logger():
    return logger

def initialize_logger(engine, min_db_level="INFO"):
    # Create the log_entries table
    Base.metadata.create_all(engine)
    
    # Add SQLAlchemy handler
    db_handler = SQLAlchemyLogHandler(engine)
    logger.add(db_handler.write, level=min_db_level)
    return logger
