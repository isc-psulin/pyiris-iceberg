import sys
import traceback
from loguru import logger

from irisiceberg.main import IcebergIRIS
from irisiceberg.utils import Configuration
import pyiceberg

sys.path.append("./configs")
import testing_configs

def get_config(config_name: str):
    conf = getattr(testing_configs, config_name)

    if not conf:
        print(f"No config named {config_name}")
        exit()
    
    return Configuration(**conf)

def create_IRISIceberg(config: Configuration):

    ice = IcebergIRIS("test", config)
    ice.iris.create_engine()
    return ice 

def purge_table(tablename: str, config_name: str):
    
    config = get_config(config_name)
    ice = create_IRISIceberg(config)
    try:
        ice.iceberg.catalog.purge_table(tablename)
    except pyiceberg.exceptions.NoSuchTableError as ex:
        logger.error(f"Cannot purge table {tablename}:  {ex}")
        #logger.error(f"Cannot purge table {tablename} because it does not exist")
    
def initial_table_sync(tablename, config_name: str):

    config = get_config(config_name)
    ice = create_IRISIceberg(config)
    ice.initial_table_sync(tablename)

    # Show some of the data from the new table
    ice_table = ice.iceberg.load_table(tablename)
    data = ice_table.scan(limit=100).to_pandas()
    
    print(data)

def update_table(tablename, config_name: str, clause: str = ""):
    config = get_config(config_name)
    ice = create_IRISIceberg(config)
    ice.update_iceberg_table(config.table_name, config.sql_clause)

if __name__ == "__main__":

    command = sys.argv[1]
    args = sys.argv[2:4]
    #cli_overrides = sys.argv[3:]
    # print(cli_overrides)
    # print(Configuration().model_dump())
    # print(command, *args)
    func = locals().get(command)
    if func:
        func(*args)
    else:
        logger.error(f"Command {command} not found")
