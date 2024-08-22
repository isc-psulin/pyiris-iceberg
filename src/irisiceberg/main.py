# Third party
import pyiceberg.table
import pyiceberg
import pandas as pd
import pyarrow as pa
from pyiceberg.catalog.sql import  SqlCatalog
from sqlalchemy import  MetaData, Engine

# Local package
import irisiceberg.utils as utils
from irisiceberg.utils import sqlalchemy_to_iceberg_schema, get_alchemy_engine, get_from_list, read_sql_to_df, split_sql
from irisiceberg.utils import create_iceberg_jobs_table, initialize_logger, get_logger, logger
from irisiceberg.utils import Configuration, IRIS_Config, IcebergJob
from datetime import datetime
from sqlalchemy.orm import sessionmaker

# TODO - move this to a config file
# Used is no config is provided when creating IRISIceberg
ICEBERG_IRIS_CONFIG_TABLE = "IcebergConfig"

class IRIS:

    def __init__(self, config: Configuration):
        self.config = config
        self.engine = None # -> Engine
        self.metadata = None # -> Metadata

    def create_engine(self):
        self.engine = get_alchemy_engine(self.config)
        initialize_logger(self.engine)
        self.logger = logger
    
    def get_odbc_connection(self):
        server = utils.get_from_list(self.config.servers, self.config.src_server)
        conn = utils.get_odbc_connection(server)
        return conn

    def connect(self): # -> Connection
        if not self.engine:
            self.engine = get_alchemy_engine(self.config)
        return self.engine.connect()

    def disconnect(self):
        self.engine.close()

    def load_table_data(self, tablename):
        """Deprecated"""
        # Really big assumption that this all fits into memory!
        # TODO - change this tinto a generator
        iris_data = pd.read_sql(f"select * from {tablename}", self.connect())
        return iris_data
    
    def get_server(self) -> IRIS_Config:
        server = get_from_list(self.config.servers, self.config.src_server)
        return server
    
    def load_metadata(self):
        self.metadata = MetaData()
        server = self.get_server()
        schemas = server.schemas
        if schemas:
            for schema in schemas:
                self.metadata.reflect(self.engine, schema)
                get_logger().debug(f"Getting Metadata for {schema} - {len(self.metadata.tables)} tables in metadata")
        else:
            # If the schemas list is empty, load from default schema
            self.metadata.reflect(self.engine)

    def get_table_stats(self, tablename, clause):
        
        partition_fld = self.config.partition_field
        where = f"WHERE {clause}" if clause else ""
        sql = f"SELECT Count(*) row_count, Min({partition_fld}) min_val, Max({partition_fld}) max_val from {tablename} {where}"
        df = pd.read_sql(sql, self.connect())
        return int(df['row_count'][0]), int(df['min_val'][0]), int(df['max_val'][0])
        
class Iceberg():
    def __init__(self, config: Configuration):
        self.config = config
        #self.iris = iris

        target_iceberg =  get_from_list(self.config.icebergs, self.config.target_iceberg) # -> Iceberg_Config

        # The configuration has to match the expected fields for it's particular type
        self.catalog = SqlCatalog(**dict(target_iceberg))
    
    def load_table(self, tablename: str) -> pyiceberg.table.Table:
        ''' 
        Load the table from iceberg using the catalog if it exists
        '''
        table = self.catalog.load_table(tablename)
        return table

    

class IcebergIRIS:
    def __init__(self, name: str = "", config: Configuration = None):
        self.name = name

        if config:
            self.config = config
        else:
            # TODO - load the config using the name from IcebergConfig
            self.config = self.load_config(name)

        self.iris = IRIS(self.config)
        self.iceberg = Iceberg(self.config)
    
    def update_iceberg_table(self, tablename: str, clause: str = ""):
        
        iceberg_table = self.iceberg.load_table(tablename)
        partition_size = self.config.table_chunksize
        clause = self.config.sql_clause

        # Ensure the IceBergJobs table exists
        create_iceberg_jobs_table(self.iris.engine)

        # Create a session
        Session = sessionmaker(bind=self.iris.engine)
        session = Session()

        # This is the DB-API library connection
        connection, _ = self.iris.get_odbc_connection()
        
        # Get initial stats
        row_count, min_id, max_id = self.iris.get_table_stats(tablename, clause)
        
        start_time = datetime.now()

        for iris_data in read_sql_to_df(connection, tablename, clause=clause, chunksize=partition_size, metadata=self.iris.metadata):
        
            # Downcast timestamps in the DataFrame
            iris_data = utils.downcast_timestamps(iris_data)
            arrow_data = pa.Table.from_pandas(iris_data)
            get_logger().info(f"Loaded  {arrow_data.num_rows}  from {tablename}")

            # iceberg_table.overwrite Could use this for first table write, would handle mid update fails as a start over.
            iceberg_table.append(arrow_data)
            
            get_logger().info(f"Appended to iceberg table")

            # Record job summary for each append operation
            end_time = datetime.now()
            job_summary = IcebergJob(
                timestamp=end_time,
                job_name=f"update_{tablename}",
                action_name="append",
                tablename=tablename,
                catalog_name=self.iceberg.catalog.name,
                src_min_id=iris_data[self.config.partition_field].min(),
                src_max_id=iris_data[self.config.partition_field].max(),
                src_timestamp=start_time
            )
            session.add(job_summary)
            session.commit()

            start_time = end_time  # Update start_time for the next iteration

        session.close()

        get_logger().info(f"Completed updating and recording job summaries for {tablename}")

    def initial_table_sync(self, tablename: str, clause: str = ""):
        
        # Create table, deleting if it exists
        iceberg_table = self.create_iceberg_table(tablename)
        get_logger().info(f"Created table {tablename}")

        # Load data from IRIS table
        #iris_data = self.iris.load_table_data(tablename)
        self.update_iceberg_table(tablename=tablename, clause=clause)

    def purge_table(self, tablename: str):
        '''
        Purge the table from iceberg
        '''
        try:
            self.catalog.purge_table(tablename)
        except pyiceberg.exceptions.NoSuchTableError as ex:
            get_logger().error(f"Cannot purge table {tablename}:  {ex}")

    def create_iceberg_table(self, tablename: str):
        '''
        1. Delete the table if it exists 
            TODO - Confirm that the data is also deleted
        2. Load the metadata from source table to create the target schema
        3. Create iceberg schema
        4. Create the namespace if it does note exist
        5. Create the table
        '''

        # If the table exists, drop it
        if self.iceberg.catalog.table_exists(tablename):
            self.iceberg.catalog.drop_table(tablename)
        
        if not self.iris.metadata:
            self.iris.load_metadata()

        schema = self.create_table_schema(tablename)   
        
        # Create the namespace
        #tablename_only = tablename.split(".")[-1]
        namespace = ".".join(tablename.split(".")[:-1])
        self.iceberg.catalog.create_namespace_if_not_exists(namespace)

        # Create the table
        location = self.iceberg.catalog.properties.get("location")
        if location:
            table = self.iceberg.catalog.create_table(identifier=tablename,schema=schema, location=location)
        else:
            table = self.iceberg.catalog.create_table(identifier=tablename,schema=schema)
        
        return table 

    def create_table_schema(self, tablename: str):
         table = self.iris.metadata.tables[tablename]
         schema = sqlalchemy_to_iceberg_schema(table)
         return schema
    
    def load_config(self, name: str): 
        raise NotImplementedError

