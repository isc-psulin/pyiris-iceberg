"""
This script will install all the tables necessary for running the iris-iceberg library.

At a high level it requires:
1. Tables for iceberg catalog, just 2 of them
2. Tables for the application: logs, data update records, etc...
"""

from sqlalchemy import create_engine
from pyiceberg.catalog.sql import SQLCatalog
from pyiceberg.catalog.sql_catalog import SQLAlchemyTableMetadata, SQLAlchemyNamespaceMetadata

# install iceberg tables
def install_iceberg_catalog_tables(connection_string):
    """
    Uses the SQLAlchemy models from SQLCatalog in pyiceberg library to create tables for the catalog
    """
    engine = create_engine(connection_string)
    
    # Create the tables
    SQLAlchemyTableMetadata.__table__.create(engine, checkfirst=True)
    SQLAlchemyNamespaceMetadata.__table__.create(engine, checkfirst=True)
    
    print("Iceberg catalog tables created successfully.")

