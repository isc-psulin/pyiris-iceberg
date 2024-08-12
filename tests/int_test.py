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

ice = create_IRISIceberg()
ice.initial_table_sync("FS.AccountMaster")