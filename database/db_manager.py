# Author: StudyingBelial | Student ID: 1234567
# Module: UFCF8S-30-2 Advanced Software Development

"""
database/db_manager.py — Singleton database connection manager for HCBS.

All SQL access goes through this module to ensure a single, consistent
connection is used throughout the application's lifetime.
"""

import sqlite3
import os
from config import DATABASE_PATH, BASE_DIR


class DBManager:
    """Manages a single SQLite connection for the lifetime of the application."""

    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connection = None
        return cls._instance

    # ── Connection lifecycle ──────────────────────────────────────────────────

    def connect(self) -> None:
        """Open the database connection, creating the data directory if needed."""
        data_dir = os.path.dirname(DATABASE_PATH)
        os.makedirs(data_dir, exist_ok=True)

        self._connection = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row  # rows behave like dicts
        self._connection.execute("PRAGMA foreign_keys = ON")

    def close(self) -> None:
        """Close the connection gracefully."""
        if self._connection:
            self._connection.close()
            self._connection = None

    @property
    def conn(self) -> sqlite3.Connection:
        if self._connection is None:
            self.connect()
        return self._connection

    # ── Schema initialisation ─────────────────────────────────────────────────

    def init_schema(self) -> None:
        """Execute schema.sql to create all tables and indexes."""
        schema_path = os.path.join(BASE_DIR, "database", "schema.sql")
        with open(schema_path, "r") as f:
            sql = f.read()
        self.conn.executescript(sql)
        self.conn.commit()

    # ── Query helpers ─────────────────────────────────────────────────────────

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a single statement (INSERT / UPDATE / DELETE)."""
        cursor = self.conn.execute(sql, params)
        self.conn.commit()
        return cursor

    def fetchone(self, sql: str, params: tuple = ()):
        """Return a single Row or None."""
        return self.conn.execute(sql, params).fetchone()

    def fetchall(self, sql: str, params: tuple = ()):
        """Return a list of Row objects."""
        return self.conn.execute(sql, params).fetchall()

    def executemany(self, sql: str, data: list) -> None:
        """Execute a statement for multiple rows (bulk insert)."""
        self.conn.executemany(sql, data)
        self.conn.commit()

    def last_insert_id(self, cursor: sqlite3.Cursor) -> int:
        return cursor.lastrowid


# Module-level singleton for convenient import
db = DBManager()

