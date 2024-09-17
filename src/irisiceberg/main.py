import sys
import time 
import gc


# Third party
import pyiceberg.partitioning
import pyiceberg.table
import pyiceberg
import pandas as pd
import pyarrow as pa
from pyiceberg.catalog.sql import  SqlCatalog
from sqlalchemy import  MetaData, Engine
from sqlalchemy.orm import Session

# Local package
import irisiceberg.utils as utils
from irisiceberg.utils import sqlalchemy_to_iceberg_schema, get_alchemy_engine, get_from_list, read_sql_to_df, split_sql
from irisiceberg.utils import create_iceberg_catalog_tables, initialize_logger, logger
from irisiceberg.utils import Configuration, IRISConfig, IcebergJob, IcebergJobStep
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
        self.logger.debug(f"Created Engine: {self.engine.url}")

    def get_engine(self):
        if not self.engine:
            self.create_engine()
        return self.engine
    
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
    
    def get_server(self) -> IRISConfig:
        server = get_from_list(self.config.servers, self.config.src_server)
        return server
    
    def load_metadata(self):
        self.metadata = MetaData()
        server = self.get_server()
        schemas = server.schemas
        if schemas:
            for schema in schemas:
                self.metadata.reflect(self.engine, schema)
                logger.debug(f"Getting Metadata for {schema} - {len(self.metadata.tables)} tables in metadata")
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

        self.target_iceberg =  get_from_list(self.config.icebergs, self.config.target_iceberg) 

        # The configuration has to match the expected fields for it's particular type
        self.catalog = SqlCatalog(**dict(self.target_iceberg))
    
    def load_table(self, tablename: str) -> pyiceberg.table.Table:
        ''' 
        Load the table from iceberg using the catalog if it exists
        '''
        try:
            table = self.catalog.load_table(tablename)
            return table
        except pyiceberg.exceptions.NoSuchTableError as ex:
            logger.error(f"Cannot find table {tablename}:  {ex}")
            return None

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
    
    def update_iceberg_table(self, session: Session,  job: IcebergJob = None):
        
        iceberg_table = self.iceberg.load_table(self.config.target_table_name)
        if iceberg_table is None:
            logger.error(f"Cannot load table, exiting")
            sys.exit(1)

        # TODO - This should be set by the config so it can use DB-API or odbc
        partition_size = self.config.table_chunksize

        # Only Create a job if one does not already exist
        if job is None:
            # Create a session
            Session = sessionmaker(bind=self.iris.engine)
            session = Session()

            # Get initial stats
            row_count, min_id, max_id = self.iris.get_table_stats(tablename, clause)
            
            job_start_time = datetime.now()

            # Create the main job record
            job = IcebergJob(
                start_time=job_start_time,
                job_name=f"update_{tablename}",
                action_name="append",
                tablename=tablename,
                catalog_name=self.iceberg.catalog.name,
                src_row_count=row_count,
                src_min_id=min_id,
                src_max_id=max_id
            )
            session.add(job)
            session.flush()  # This will populate the job.id

        # Set the current job ID for logging
        utils.current_job_id.set(job.id)

        # TODO - This should be set by the config so it can use DB-API or odbc
        server = self.iris.get_server()
        if server.connection_type == "odbc":
            connection = self.iris.get_odbc_connection()
        else:
            connection = self.iris.engine.connect()
        
        for iris_data in read_sql_to_df(connection, self.config.source_table_name, 
                                        clause = self.config.sql_clause, chunksize=partition_size,
                                        metadata=self.iris.metadata):
        
            step_start_time = datetime.now()

            # Downcast timestamps in the DataFrame
            iris_data = utils.downcast_timestamps(iris_data)
            arrow_data = pa.Table.from_pandas(iris_data)
            
            # iceberg_table.overwrite Could use this for first table write, would handle mid update fails as a start over.
            start_time = time.time()
            iceberg_table.append(arrow_data)
            load_time = time.time() - start_time
            logger.info(f"Appended {arrow_data.num_rows} record to iceberg table in {load_time:.2f} seconds at {arrow_data.num_rows/load_time} per sec")
            
            # Record job step
            step_end_time = datetime.now()
            minval = 0 if pd.isna(iris_data[self.config.partition_field].min()) else iris_data[self.config.partition_field].min()
            maxval = 0 if pd.isna(iris_data[self.config.partition_field].max()) else iris_data[self.config.partition_field].max()
            job_step = IcebergJobStep(
                job_id=job.id,
                start_time=step_start_time,
                end_time=step_end_time,
                src_min_id=minval,
                src_max_id=maxval,
                src_timestamp=step_start_time
            )
            session.add(job_step)
            session.commit()

            del iris_data, arrow_data
            gc.collect()
            

        # Update the main job record with the end time
        job.end_time = datetime.now()
        session.commit()
        session.close()

        # Reset the current job ID
        utils.current_job_id.set(None)

        logger.info(f"Completed updating and recording job summaries for {self.config.target_table_name}")

    def initial_table_sync(self):
        """ This function creates all the required tables and does an initial load of data.
        This is a good method for quickly testing the code without needing to setup a catalog or create the iceberg tables.
        This should not be used in production and will drop any existing tables and delete all data in that table.
        Outside of testing, update_iceberg_table should be used for moving data and the required tables should be created
        as a separate Devops process.
        """
        # Create iceberg catalog tables if they do not exist
        create_iceberg_catalog_tables(self.iceberg.target_iceberg)

        # Ensure the Iceberg tables exist
        self.create_iceberg_table(self.config.target_table_name)

        # Create a session
        Session = sessionmaker(bind=self.iris.engine)
        session = Session()

        job_start_time = datetime.now()

        # Create the main job record
        job = IcebergJob(
            start_time=job_start_time,
            job_name=f"initial_sync_{self.config.source_table_name}",
            action_name="initial_sync",
            tablename=self.config.source_table_name,
            catalog_name=self.iceberg.catalog.name
        )
        session.add(job)
        session.flush()  # This will populate the job.id
        #session.refresh(job)
         
        # Create table, deleting if it exists
        iceberg_table = self.create_iceberg_table(self.config.target_table_name)
        logger.info(f"Created table {self.config.target_table_name}")


        self.update_iceberg_table(job=job, session=session)

        # Update the main job record with the end time
        job.end_time = datetime.now()
        session.commit()
        session.close()

    def purge_table(self, tablename: str):
        '''
        Purge the table from iceberg
        '''
        try:
            self.catalog.purge_table(tablename)
        except pyiceberg.exceptions.NoSuchTableError as ex:
            logger.error(f"Cannot purge table {tablename}:  {ex}")

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
        print(f"Iceberg schema {schema}")
        logger.info(f"Iceberg schema {schema}")

        # Create the namespace
        #tablename_only = tablename.split(".")[-1]
        namespace = ".".join(tablename.split(".")[:-1])
        self.iceberg.catalog.create_namespace_if_not_exists(namespace)

        # Create the table
        location = self.iceberg.catalog.properties.get("location")

        #partition_spec = pyiceberg.partitioning.PartitionSpec(pyiceberg.partitioning.PartitionField(name='ID'))
        print(schema)
        if location:
            logger.debug(f"TABLENAME _ {tablename}")
            table = self.iceberg.catalog.create_table(identifier=tablename,schema=schema, 
                                                      location=location)
        else:
            table = self.iceberg.catalog.create_table(identifier=tablename,schema=schema)
        
        return table 

    def create_table_schema(self, tablename: str):
         table = self.iris.metadata.tables[tablename]
         schema = sqlalchemy_to_iceberg_schema(table)
         return schema


