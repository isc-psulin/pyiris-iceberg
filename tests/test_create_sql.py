#!/usr/bin/env python3

import unittest
from sqlalchemy import inspect, create_engine
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from install.create_sql import install_iceberg_catalog_tables

class TestCreateSQL(unittest.TestCase):
    def setUp(self):
        self.connection_string = "sqlite:///:memory:"
        self.engine = create_engine(self.connection_string)
        install_iceberg_catalog_tables(self.connection_string)
        self.inspector = inspect(self.engine)

    def tearDown(self):
        self.engine.dispose()

    def test_tables_created(self):
        expected_tables = ['iceberg_tables', 'iceberg_namespaces']
        actual_tables = self.inspector.get_table_names()
        for table in expected_tables:
            self.assertIn(table, actual_tables, f"Table {table} was not created")

    def test_iceberg_tables_structure(self):
        expected_columns = {
            'catalog_name': {'type': 'VARCHAR', 'nullable': False},
            'table_namespace': {'type': 'VARCHAR', 'nullable': False},
            'table_name': {'type': 'VARCHAR', 'nullable': False},
            'metadata_location': {'type': 'VARCHAR', 'nullable': False},
            'previous_metadata_location': {'type': 'VARCHAR', 'nullable': True}
        }
        self._assert_table_structure('iceberg_tables', expected_columns)

    def test_iceberg_namespaces_structure(self):
        expected_columns = {
            'catalog_name': {'type': 'VARCHAR', 'nullable': False},
            'namespace': {'type': 'VARCHAR', 'nullable': False},
            'properties': {'type': 'VARCHAR', 'nullable': True}
        }
        self._assert_table_structure('iceberg_namespaces', expected_columns)

    def _assert_table_structure(self, table_name, expected_columns):
        columns = self.inspector.get_columns(table_name)
        for column in columns:
            expected = expected_columns[column['name']]
            self.assertIn(expected['type'], str(column['type']).upper(), f"Incorrect type for {column['name']} in {table_name}")
            self.assertEqual(expected['nullable'], column['nullable'], f"Incorrect nullable for {column['name']} in {table_name}")

if __name__ == '__main__':
    unittest.main()
