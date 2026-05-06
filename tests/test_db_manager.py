"""
tests/test_db_manager.py — Unit tests for the DB manager.
"""

import unittest
import sys, os
import sqlite3
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database.db_manager import DBManager, db
from config import BASE_DIR

class TestDBManager(unittest.TestCase):

    def setUp(self):
        """Reset the singleton instance for each test."""
        DBManager._instance = None
        self.db_manager = DBManager()
        # Use an in-memory database
        self.db_manager._connection = sqlite3.connect(":memory:", check_same_thread=False)
        self.db_manager._connection.row_factory = sqlite3.Row
        self.db_manager._connection.execute("PRAGMA foreign_keys = ON")
        
        # We need to test schema creation so we do not call init_schema() here directly in all tests
        # Create a simple table for general testing
        self.db_manager.execute("CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY, name TEXT)")
        
    def tearDown(self):
        self.db_manager.close()

    def test_singleton(self):
        """Test that DBManager is a singleton."""
        db1 = DBManager()
        db2 = DBManager()
        self.assertIs(db1, db2)

    def test_connect_and_close(self):
        """Test connecting and closing the database."""
        # Using a fresh manager instance that doesn't have an injected in-memory db
        DBManager._instance = None
        manager = DBManager()
        
        # mock DATABASE_PATH for this test to be in-memory or temporary
        # But connect hardcodes DATABASE_PATH from config. We will just test if close works.
        manager._connection = sqlite3.connect(":memory:", check_same_thread=False)
        self.assertIsNotNone(manager._connection)
        
        manager.close()
        self.assertIsNone(manager._connection)

    def test_conn_property(self):
        """Test that the conn property returns a valid connection."""
        conn = self.db_manager.conn
        self.assertIsInstance(conn, sqlite3.Connection)

    def test_execute_and_fetchone(self):
        """Test execute and fetchone methods."""
        self.db_manager.execute("INSERT INTO test_table (name) VALUES (?)", ("Test 1",))
        row = self.db_manager.fetchone("SELECT * FROM test_table WHERE name = ?", ("Test 1",))
        self.assertIsNotNone(row)
        self.assertEqual(row["name"], "Test 1")

    def test_fetchall(self):
        """Test fetchall method."""
        self.db_manager.execute("INSERT INTO test_table (name) VALUES (?)", ("Test 1",))
        self.db_manager.execute("INSERT INTO test_table (name) VALUES (?)", ("Test 2",))
        rows = self.db_manager.fetchall("SELECT * FROM test_table")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["name"], "Test 1")
        self.assertEqual(rows[1]["name"], "Test 2")

    def test_executemany(self):
        """Test executemany method."""
        data = [("Test 1",), ("Test 2",), ("Test 3",)]
        self.db_manager.executemany("INSERT INTO test_table (name) VALUES (?)", data)
        rows = self.db_manager.fetchall("SELECT * FROM test_table")
        self.assertEqual(len(rows), 3)

    def test_last_insert_id(self):
        """Test last_insert_id method."""
        cursor = self.db_manager.execute("INSERT INTO test_table (name) VALUES (?)", ("Test ID",))
        last_id = self.db_manager.last_insert_id(cursor)
        self.assertEqual(last_id, 1) # Assuming it's the first insert in the setUp's isolated db instance
        
        cursor2 = self.db_manager.execute("INSERT INTO test_table (name) VALUES (?)", ("Test ID 2",))
        last_id2 = self.db_manager.last_insert_id(cursor2)
        self.assertEqual(last_id2, 2)

    def test_init_schema(self):
        """Test that init_schema executes the schema correctly."""
        # Using a fresh in-memory db
        DBManager._instance = None
        manager = DBManager()
        manager._connection = sqlite3.connect(":memory:", check_same_thread=False)
        manager._connection.row_factory = sqlite3.Row
        
        # Call init_schema
        manager.init_schema()
        
        # Verify that a table from schema.sql exists (e.g., 'users')
        row = manager.fetchone("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        self.assertIsNotNone(row)
        self.assertEqual(row["name"], "users")


if __name__ == "__main__":
    unittest.main()
