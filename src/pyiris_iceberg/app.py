import os
import sys
import json 
from collections import defaultdict
import importlib.util
import traceback

import pyiceberg
from dotenv import load_dotenv

from pyiris_iceberg.main import IcebergIRIS, Iceberg
from pyiris_iceberg.utils import Configuration, logger

load_dotenv(verbose=True)
CONFIG_PATH = os.getenv("IRISICE_CONFIG_PATH")
#print(f"CONFIG_PATH =  {CONFIG_PATH}")

def create_IRISIceberg(config: Configuration):

    ice = IcebergIRIS("test", config)
    ice.iris.create_engine()
    
    return ice 

def purge_table(config: Configuration):

    tablename = config.target_table_name
    ice = create_IRISIceberg(config)
    try:
        ice.iceberg.catalog.purge_table(tablename)
        logger.info(f"Purged table {tablename}")
    except pyiceberg.exceptions.NoSuchTableError as ex:
        logger.error(f"Cannot purge table {tablename}:  {ex}")
        #logger.error(f"Cannot purge table {tablename} because it does not exist")
    
def initial_table_sync(config: Configuration):

    tablename = config.source_table_name
    ice = create_IRISIceberg(config)
    ice.initial_table_sync()

    # Show some of the data from the new table
    ice_table = ice.iceberg.load_table(config.target_table_name)
    data = ice_table.scan(limit=100).to_pandas()
    
    print(data)

def show_table_data_schema(config: Configuration):

    tablename = config.target_table_name
    ice = create_IRISIceberg(config)

    # Show some of the data from the new table
    ice_table = ice.iceberg.load_table(tablename)
    
    data = ice_table.scan(limit=100).to_pandas()
    
    print(ice_table.schema())
    print(data)

def list_tables(config: Configuration):

    tables = []
    try:
        ice = Iceberg(config)
        namespaces = ice.catalog.list_namespaces()
        
        tables_with_ns = defaultdict(list)
        for ns in namespaces:
            tables_with_ns[ns] = ice.catalog.list_tables(ns) 
        
        for ns, tablename in tables_with_ns.items():
            logger.info(f"{tablename}")
            if tablename:
                tables.append(f"{ns}.{tablename}")

        print(tables)
    except Exception as ex:
        traceback.print_exc()
        raise ex
    
    return tables

def select_all(config: Configuration):
    ice = Iceberg(config)
    table = ice.load_table(config.target_table_name)
    df = table.scan(limit=100000).to_pandas()
    print(df)
    return df

def update_table(config: Configuration):

    ice = create_IRISIceberg(config)
    ice.update_iceberg_table()

def load_config(config_path: str = ""):
    
    if not config_path:
        config_path = CONFIG_PATH

    config = json.load(open(config_path))
    logger.info(f"Loaded config from {config_path} : {config}")
    config = Configuration(**config)
    return config 

def main(config_path: str = None):

    config = Configuration()
    config_path = config_path if config_path else config.config_path

    if config_path:
        config_str = open(config_path).read()
    elif os.path.exists(CONFIG_PATH):
        config_str = open(CONFIG_PATH).read()
    else:
        logger.error(f"No Config provided")
        sys.exit(1)
    
    # # config is determined in this order: passed as arg, passed as CLI arg
    # if config_path:
    #     config_str = open(config_path).read()
    # else:
    #     # Check if it is a CLI arg. This is done autmotically by Pydantic
    #     config = Configuration()
    #     # Check if it can be loaded from ENV VAR
    #     if not config.config_path and os.path.exists(CONFIG_PATH):
    #         config_str = open(CONFIG_PATH).read()

    # if not config_str:
    #     logger.error(f"No Config provided")
    #     sys.exit(1)
    
    try:
        config_dict = json.loads(config_str)
    except Exception as ex:
        logger.error(f"Failed to load config as JSON: {ex}")
        sys.exit(1)

    config = Configuration(**config_dict)
    
    job_type_func = globals().get(config.job_type)
    if not job_type_func:
        logger.error(f"Cannot find job type {config.job_type}")
        sys.exit(1)

    job_type_func(config)
   
if __name__ == "__main__":
    main()