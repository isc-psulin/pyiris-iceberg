import glob
import os
import iris
import pandas as pd
from sqlalchemy import create_engine
from iris import ipm
import json


# switch namespace to the %SYS namespace
iris.system.Process.SetNamespace("%SYS")

# set credentials to not expire
iris.cls('Security.Users').UnExpireUserPasswords("*")

# switch namespace to IRISAPP built by merge.cpf
iris.system.Process.SetNamespace("IRISAPP")

# Load the config into a global
with open("/home/irisowner/dev/local_testing_config.json") as fi:
    config = fi.read()

glob_config=iris.gref('icebergConfig')
glob_config.set(config)

# load ipm package listed in module.xml
#iris.cls('%ZPM.PackageManager').Shell("load /home/irisowner/dev -v")
print("Starting load of IPM")
assert ipm('load /home/irisowner/dev -v')
print("Completed load of IPM")

print("Starting load of data")
# load demo data
engine = create_engine('iris+emb:///')
# list all csv files in the demo data folder
for files in glob.glob('/home/irisowner/dev/data/*.csv'):
    # get the file name without the extension
    table_name = os.path.splitext(os.path.basename(files))[0]
    # load the csv file into a pandas dataframe
    df = pd.read_csv(files)
    # write the dataframe to IRIS
    df.to_sql(table_name, engine, if_exists='replace', index=False, schema='iceberg_demo')

print("Finished load of data")

# import subprocess

# def install(package):
#     results = subprocess.run(["pip", "install", package])
#     print(f"Results {results}")

 
# install("/home/irisowner/dev/")

