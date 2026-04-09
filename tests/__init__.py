"""
Tests package for Horizon Booking System.
This module provides a unified entry point for running all tests.
"""

import pytest
import sys
import os

def run():
    """
    Runs all tests in the tests/ directory using pytest.
    This function can be imported and called from other scripts.
    
    Returns:
        int: The exit code from pytest.main()
    """
    # Identify the tests directory (the directory containing this file)
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Execute pytest. 
    # We include sys.argv[1:] to pass through any command line arguments 
    # (like -v or -s) when run from the command line.
    return pytest.main([tests_dir] + sys.argv[1:])

if __name__ == "__main__":
    # This block allows the module to be executed directly:
    # python tests/__init__.py
    # Or as a module:
    # python -m tests
    sys.exit(run())
