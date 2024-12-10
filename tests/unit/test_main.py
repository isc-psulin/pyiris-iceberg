import os
import sys
from pyiris_iceberg.main import IcebergIRIS
import pyiris_iceberg.utils as utils
import tests.fixtures.testing_configs as testing_configs

# sys.path.append("./fixtures")
# import testing_configs
from pprint import pprint 

def test_create_IRISIceberg():

    config = utils.Configuration(**testing_configs.iris_src_local_target)
    ice = IcebergIRIS("test", config)
    assert isinstance(ice, IcebergIRIS)

def test_connect_to_source_server():

    config = utils.Configuration(**testing_configs.iris_src_local_target)
    ice = IcebergIRIS("test", config)
    ice.iris.create_engine()
    connection = ice.iris.connect()
    assert connection.closed == False

if __name__ == "__main__":
    test_create_IRISIceberg()
    test_connect_to_source_server()

