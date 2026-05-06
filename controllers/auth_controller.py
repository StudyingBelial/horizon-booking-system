# Author: StudyingBelial | Student ID: 1234567
# Module: UFCF8S-30-2 Advanced Software Development

"""
controllers/auth_controller.py — Handles login and session state.
"""

from database.db_manager import db
from models.user import User
from utils.helpers import verify_password


class AuthController:
    """Validates credentials and returns the appropriate User subclass."""

    _current_user = None   # Module-level session holder

    @classmethod
    def login(cls, username: str, password: str):
        """
        Attempt login.
        Returns a User subclass instance on success, raises ValueError on failure.
        """
        if not username or not password:
            raise ValueError("Username and password are required.")

        row = db.fetchone(
            "SELECT * FROM users WHERE username=?", (username.strip(),)
        )
        if row is None:
            raise ValueError("Invalid username or password.")

        if not verify_password(password, row["passwordHash"]):
            raise ValueError("Invalid username or password.")

        user = User.from_row(row)
        cls._current_user = user
        return user

    @classmethod
    def logout(cls) -> None:
        cls._current_user = None

    @classmethod
    def current_user(cls):
        return cls._current_user

    @classmethod
    def is_logged_in(cls) -> bool:
        return cls._current_user is not None

    @classmethod
    def require_role(cls, *roles: str) -> None:
        """Raise PermissionError if current user's role is not in *roles*."""
        user = cls._current_user
        if user is None:
            raise PermissionError("Not logged in.")
        if user.role not in roles:
            raise PermissionError(
                f"Access denied. Required role(s): {roles}. "
                f"Your role: {user.role}"
            )

