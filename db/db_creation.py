"""
db_creation.py
--------------
Reads the SQL statements from schema.sql and executes them
against the SQLite database defined in db_access.py.

Usage:
    python db_creation.py          # creates tables (skips if they exist)
    python db_creation.py --force  # drops all tables first, then recreates
"""

import os
import sys
import sqlite3

# Resolve paths relative to this script's directory
_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_DIR, "hcbs.db")
QUERIES_PATH = os.path.join(_DIR, "schema.sql")


def read_queries(path: str) -> str:
    """Read the SQL file and return its contents as a string."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def create_database(force: bool = False) -> None:
    """
    Create every table defined in schema.sql.

    Parameters
    ----------
    force : bool
        If True, drop all existing tables before recreating them.
    """
    sql = read_queries(QUERIES_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    if force:
        print("[db_creation] --force flag detected: dropping existing tables ...")
        # Fetch existing table names and drop them in reverse order
        # to avoid FK-constraint errors.
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'"
        ).fetchall()
        conn.execute("PRAGMA foreign_keys = OFF")
        for (table_name,) in reversed(tables):
            conn.execute(f"DROP TABLE IF EXISTS [{table_name}]")
            print(f"  dropped: {table_name}")
        conn.execute("PRAGMA foreign_keys = ON")
        conn.commit()

    try:
        conn.executescript(sql)
        conn.commit()
        print("[db_creation] OK - All tables created successfully.")
    except sqlite3.OperationalError as e:
        # e.g. "table users already exists"
        print(f"[db_creation] WARNING - SQLite error: {e}")
        print("  Hint: use --force to drop and recreate all tables.")
    finally:
        conn.close()

    # Quick verification — list the tables that now exist
    conn = sqlite3.connect(DB_PATH)
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence' ORDER BY name"
    ).fetchall()
    conn.close()

    print(f"\n[db_creation] Tables in {os.path.basename(DB_PATH)}:")
    for (t,) in tables:
        print(f"  • {t}")


if __name__ == "__main__":
    force = "--force" in sys.argv
    create_database(force=force)