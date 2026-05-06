# Author: StudyingBelial | Student ID: 1234567
# Module: UFCF8S-30-2 Advanced Software Development

"""
main.py — Entry point for the Horizon Cinemas Booking System (HCBS).

Run with:
    python main.py

Sequence:
    1. Initialise (or reuse) the SQLite database
    2. Seed initial data if tables are empty
    3. Launch the Tkinter Login UI
"""

import sys
import os

# ── Ensure the project root is on sys.path ────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.db_manager import db
from database.seed_data import seed
from ui.login_ui import LoginUI


def main():
    # ── 1. Connect & initialise schema ────────────────────────────────────────
    db.connect()
    db.init_schema()
    print("[HCBS] Database initialised.")

    # ── 2. Seed data ──────────────────────────────────────────────────────────
    seed()

    # ── 3. Launch GUI ─────────────────────────────────────────────────────────
    print("[HCBS] Launching Horizon Cinemas Booking System…")
    app = LoginUI()
    app.mainloop()

    # ── 4. Clean up ───────────────────────────────────────────────────────────
    db.close()
    print("[HCBS] Shutdown complete.")


if __name__ == "__main__":
    main()
