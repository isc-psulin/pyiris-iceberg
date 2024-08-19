import sys

from irisiceberg.main import IcebergIRIS
from irisiceberg.utils import Configuration

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


def delete_table(tablename: str, config_name: str):
    
    config = get_config(config_name)
    ice = create_IRISIceberg(config)
    ice.iceberg.catalog.purge_table(tablename)


def replicate_table(tablename, config_name: str):

    config = get_config(config_name)
    ice = create_IRISIceberg(config)
    ice.initial_table_sync(tablename)

    # Show some of the data from the new table
    ice_table = ice.iceberg.load_table(tablename)
    data = ice_table.scan(limit=100).to_pandas()
    print(data)

if __name__ == "__main__":
    print(sys.argv)
    command = sys.argv[1]
    args = sys.argv[2:]
    print(command, *args)
    func = locals().get(command)
    func(*args)
