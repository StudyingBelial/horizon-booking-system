"""
config.py — Global configuration for HCBS.
"""

import os

# Root of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# SQLite database path (Can be overridden by DATABASE_URL environment variable)
# Note: Render often provides DATABASE_URL for Postgres, but here we use it for the SQLite file path if provided.
DATABASE_PATH = os.getenv("DATABASE_URL", os.path.join(BASE_DIR, "data", "hcbs.db"))

# Server Port (Required for Render Web Services)
PORT = int(os.getenv("PORT", 3000))

# Application name displayed in GUI title bars
APP_NAME = "Horizon Cinemas Booking System"

# ── Pricing multipliers ──────────────────────────────────────────────────────
UPPER_GALLERY_PREMIUM = 1.20  # +20 % over base
VIP_PREMIUM = 1.44  # base × 1.2 × 1.2  (applied on top of upper)

# Cancellation refund rate (50 %)
CANCELLATION_REFUND_RATE = 0.50

# Maximum days in advance a booking may be made
MAX_ADVANCE_BOOKING_DAYS = 7

# Minimum days before showDate that cancellation is allowed (> 1 day away)
MIN_CANCEL_DAYS_BEFORE_SHOW = 1
