import sys

from irisiceberg.main import IcebergIRIS
from irisiceberg.utils import Configuration

sys.path.append("./configs")
import testing_configs

def create_IRISIceberg():

    target = testing_configs.local_src_azure_target
    #target = testing_configs.iris_src_local_target
    config = Configuration(**target)
    ice = IcebergIRIS("test", config)
    ice.iris.create_engine()
    return ice 

tablename = "FS.AccountMaster"
iris_ice = create_IRISIceberg()
iris_ice.initial_table_sync(tablename)

ice_table = iris_ice.iceberg.load_table(tablename)
data = ice_table.scan().to_pandas()
print(data)