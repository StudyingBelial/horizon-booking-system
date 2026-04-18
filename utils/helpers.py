"""
utils/helpers.py — Utility functions used across HCBS.
"""

import hashlib
import uuid
import re
from datetime import datetime


# ── Password hashing ─────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    """Return SHA-256 hex digest of the plain-text password."""
    return hashlib.sha256(plain.encode("utf-8")).hexdigest()


def verify_password(plain: str, hashed: str) -> bool:
    """Check whether *plain* matches *hashed*."""
    return hash_password(plain) == hashed


# ── Booking reference generation ─────────────────────────────────────────────

def generate_booking_ref() -> str:
    """Return a short, uppercase, unique booking reference (e.g. HCB-A1B2C3D4)."""
    short = uuid.uuid4().hex[:8].upper()
    return f"HCB-{short}"


# ── Date / time helpers ──────────────────────────────────────────────────────

def today() -> datetime.date:
    return datetime.now().date()


def parse_date(date_str: str) -> datetime.date:
    """Parse 'YYYY-MM-DD' string to date object."""
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def format_date(d) -> str:
    """Format date object to 'YYYY-MM-DD'."""
    return d.strftime("%Y-%m-%d")


def format_datetime(dt) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def now_str() -> str:
    """Current datetime as 'YYYY-MM-DD HH:MM:SS'."""
    return format_datetime(datetime.now())


# ── Input validation helpers ─────────────────────────────────────────────────

def is_valid_email(email: str) -> bool:
    pattern = r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$"
    return bool(re.match(pattern, email))


def is_non_empty(value: str) -> bool:
    return isinstance(value, str) and bool(value.strip())


# ── Currency formatting ──────────────────────────────────────────────────────

def format_currency(amount: float) -> str:
    return f"£{amount:,.2f}"
