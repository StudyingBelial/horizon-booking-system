# Author: StudyingBelial | Student ID: 1234567
# Module: UFCF8S-30-2 Advanced Software Development

import pytest
from unittest.mock import patch, MagicMock
from controllers.auth_controller import AuthController
from models.user import User, BookingStaff

@pytest.fixture(autouse=True)
def reset_auth_controller():
    """Reset the current user before each test."""
    AuthController.logout()

@patch("controllers.auth_controller.db")
@patch("controllers.auth_controller.verify_password")
@patch("models.user.User.from_row")
def test_login_success(mock_from_row, mock_verify, mock_db):
    # Setup
    mock_db.fetchone.return_value = {"username": "testuser", "passwordHash": "hashed", "role": "BookingStaff"}
    mock_verify.return_value = True
    user_obj = BookingStaff(1, "testuser", "hashed", "test@example.com", "BookingStaff")
    mock_from_row.return_value = user_obj
    
    # Execute
    user = AuthController.login("testuser", "password123")
    
    # Assert
    assert user == user_obj
    assert AuthController.current_user() == user_obj
    assert AuthController.is_logged_in() is True
    mock_db.fetchone.assert_called_once()
    mock_verify.assert_called_once_with("password123", "hashed")

def test_login_missing_credentials():
    with pytest.raises(ValueError, match="Username and password are required."):
        AuthController.login("", "password")
    
    with pytest.raises(ValueError, match="Username and password are required."):
        AuthController.login("user", "")

@patch("controllers.auth_controller.db")
def test_login_invalid_username(mock_db):
    mock_db.fetchone.return_value = None
    
    with pytest.raises(ValueError, match="Invalid username or password."):
        AuthController.login("nonexistent", "password")

@patch("controllers.auth_controller.db")
@patch("controllers.auth_controller.verify_password")
def test_login_invalid_password(mock_verify, mock_db):
    mock_db.fetchone.return_value = {"username": "testuser", "passwordHash": "hashed"}
    mock_verify.return_value = False
    
    with pytest.raises(ValueError, match="Invalid username or password."):
        AuthController.login("testuser", "wrongpassword")

def test_logout():
    AuthController._current_user = MagicMock()
    AuthController.logout()
    assert AuthController.current_user() is None
    assert AuthController.is_logged_in() is False

def test_require_role_not_logged_in():
    with pytest.raises(PermissionError, match="Not logged in."):
        AuthController.require_role("Admin")

def test_require_role_access_denied():
    user = MagicMock(spec=BookingStaff)
    user.role = "BookingStaff"
    AuthController._current_user = user
    
    with pytest.raises(PermissionError, match=r"Access denied. Required role\(s\): \('Admin',\). Your role: BookingStaff"):
        AuthController.require_role("Admin")

def test_require_role_success():
    user = MagicMock(spec=BookingStaff)
    user.role = "Admin"
    AuthController._current_user = user
    
    # Should not raise any exception
    AuthController.require_role("Admin", "Manager")

