import unittest
from sqlalchemy import inspect
from install.create_sql import install_iceberg_catalog_tables

class TestCreateSQL(unittest.TestCase):
    def test_install_iceberg_catalog_tables(self):
        # Use SQLite in-memory database for testing
        connection_string = "sqlite:///:memory:"
        
        # Call the function to create tables
        install_iceberg_catalog_tables(connection_string)
        
        # Verify that the tables were created
        engine = inspect(connection_string).engine
        inspector = inspect(engine)
        
        expected_tables = ['iceberg_tables', 'iceberg_namespaces']
        actual_tables = inspector.get_table_names()
        
        for table in expected_tables:
            self.assertIn(table, actual_tables, f"Table {table} was not created")
        
        # Verify the structure of the tables
        iceberg_tables_columns = [col['name'] for col in inspector.get_columns('iceberg_tables')]
        iceberg_namespaces_columns = [col['name'] for col in inspector.get_columns('iceberg_namespaces')]
        
        expected_iceberg_tables_columns = ['catalog_name', 'table_namespace', 'table_name', 'metadata_location', 'previous_metadata_location']
        expected_iceberg_namespaces_columns = ['catalog_name', 'namespace', 'properties']
        
        self.assertEqual(set(iceberg_tables_columns), set(expected_iceberg_tables_columns), "iceberg_tables structure is incorrect")
        self.assertEqual(set(iceberg_namespaces_columns), set(expected_iceberg_namespaces_columns), "iceberg_namespaces structure is incorrect")

if __name__ == '__main__':
    unittest.main()
