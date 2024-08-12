import sys

from irisiceberg.main import IcebergIRIS
from irisiceberg.utils import Configuration

sys.path.append("./configs")
import testing_configs

def create_IRISIceberg():

    config = Configuration(**testing_configs.iris_src_local_target)
    ice = IcebergIRIS("test", config)
    ice.iris.create_engine()
    return ice 

tablename = "FS.AccountMaster"
iris_ice = create_IRISIceberg()
iris_ice.initial_table_sync(tablename)

ice_table = iris_ice.iceberg.load_table(tablename)

print(ice_table)