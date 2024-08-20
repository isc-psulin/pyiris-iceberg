"""
This script will install all the tables necessary for running the iris-iceberg library.

At a high level it requires:
1. Tables for iceberg catalog, just 2 of them
2. Tables for the application: logs, data update records, etc...
"""

from sqlalchemy import create_engine
from pyiceberg.catalog.sql import SQLCatalog

# install iceberg tables
def install_iceberg_catalog_tables(connection_string):
    """
    Uses the SQLCatalog.create_tables() method to create tables for the catalog
    """
    engine = create_engine(connection_string)
    
    # Create the tables
    SQLCatalog.create_tables(engine)
    
    print("Iceberg catalog tables created successfully.")

