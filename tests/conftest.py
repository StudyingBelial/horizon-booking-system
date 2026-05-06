import pytest

@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    """
    Hooks into the terminal reporter to duplicate all output to test_results.txt.
    """
    # Get the terminal reporter plugin
    tr = config.pluginmanager.get_plugin("terminalreporter")
    if tr:
        # We wrap the terminal writer's write method to also write to our file
        orig_write = tr._tw.write
        
        # Open the file in write mode to refresh it every time
        f = open("test_results.txt", "w", encoding="utf-8")
        
        def new_write(content, **kwargs):
            # Write to the file (strip ANSI colors if necessary, but pytest usually 
            # handles that if not a TTY)
            f.write(content)
            f.flush()
            # Call original write to show on terminal
            orig_write(content, **kwargs)
            
        tr._tw.write = new_write
        # Store file handle in config to close it properly at the end
        config._test_results_file = f

@pytest.fixture(scope="session", autouse=True)
def init_test_db():
    """
    Ensures all tests run against an in-memory database with the schema initialized.
    This prevents 'no such table' errors in fresh environments like CI.
    """
    from database.db_manager import db
    import sqlite3
    
    # Force in-memory connection
    db._instance._connection = sqlite3.connect(":memory:", check_same_thread=False)
    db._connection.row_factory = sqlite3.Row
    db._connection.execute("PRAGMA foreign_keys = ON")
    
    # Initialize schema
    db.init_schema()
    
    yield
    
    db.close()

def pytest_unconfigure(config):
    """
    Clean up by closing the file handle.
    """
    if hasattr(config, "_test_results_file"):
        config._test_results_file.close()
