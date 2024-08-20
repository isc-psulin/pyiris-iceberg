"""
This script will install all the tables necessary for running the iris-iceberg library.

At a high level it requires:
1. Tables for iceberg catalog, just 2 of them
2. Tables for the application: logs, data update records, etc...
"""

# install iceberg tables
def install_iceberg_catalog_tables():
    """
    Uses the SQLAlchemy models from SQLCatalog in pyiceberg library to create tables for the catalog
    """

