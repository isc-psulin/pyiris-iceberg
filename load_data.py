import glob
import os
import pandas as pd
import iris 
from sqlalchemy import create_engine

iris.system.Process.SetNamespace("IRISAPP")
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