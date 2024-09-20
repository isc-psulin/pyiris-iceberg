import os
import sys
import json 
from collections import defaultdict
import importlib.util

from loguru import logger
import pyiceberg
from dotenv import load_dotenv

from irisiceberg.main import IcebergIRIS
from irisiceberg.utils import Configuration, logger

load_dotenv(verbose=True)
CONFIG_PATH = os.getenv("IRISICE_CONFIG_PATH")
print(CONFIG_PATH)

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

    ice = create_IRISIceberg(config)

    namespaces = ice.iceberg.catalog.list_namespaces()

    tables = defaultdict(list)
    for ns in namespaces:
        tables[ns] = ice.iceberg.catalog.list_tables(ns) 
    
    logger.info(f"Found {len(tables.items())} tables")
    for ns, tablename in tables.items():
        logger.info(f"{tablename}")

def update_table(config: Configuration):

    ice = create_IRISIceberg(config)
    ice.update_iceberg_table()

def load_config_old():
    # Load the module from the given path
    spec = importlib.util.spec_from_file_location('configuration', CONFIG_PATH)
    module = importlib.util.module_from_spec(spec)
    loaded = spec.loader.exec_module(module)
    
    config_dict = getattr(module, CONFIG_NAME)
    config = Configuration(**config_dict)
    return config 

def load_config():
    
    config = json.load(open(CONFIG_PATH))
    logger.info(f"Loaded config from {CONFIG_PATH}")
    config = Configuration(**config)
    return config 


def main(config_str: str = None):

    # config is detemined in this order: passed as arg, passed as CLI arg
    if not config_str:
        # Check if it is a CLI arg. This is done autmotically by Pydantic
        config = Configuration()
        config_str = config.config_string
        # Check if it can be loaded from ENV VAR
        if not config_str and os.path.exists(CONFIG_PATH):
            config_str = open(CONFIG_PATH).read()

    if not config_str:
        logger.error(f"No Config provided")
        sys.exit(1)
    
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