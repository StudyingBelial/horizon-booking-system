import os
import pytest
import sqlite3
import tempfile
from db import db_access, db_creation

@pytest.fixture(scope="session", autouse=True)
def test_db():
    # Create a temporary file for the database
    fd, temp_db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    # Patch the DB_PATH in both modules
    original_db_path_access = db_access.DB_PATH
    original_db_path_creation = db_creation.DB_PATH
    
    db_access.DB_PATH = temp_db_path
    db_creation.DB_PATH = temp_db_path
    
    # Initialize the database schema
    db_creation.create_database(force=True)
    
    # Add some seed data for common tests if needed, or leave it to specific tests
    # Let's add a test user for auth tests
    with sqlite3.connect(temp_db_path) as conn:
        conn.execute(
            "INSERT INTO users (username, password_hash, email, role, is_active) VALUES (?,?,?,?,?)",
            ("testuser", "hashed_password", "test@example.com", "admin", 1)
        )
        conn.commit()

    yield temp_db_path
    
    # Cleanup: restore paths and remove temp file
    db_access.DB_PATH = original_db_path_access
    db_creation.DB_PATH = original_db_path_creation
    
    # Try to remove the file, but don't fail if Windows is still holding it
    try:
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)
    except OSError:
        pass
