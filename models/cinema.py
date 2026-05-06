# Author: StudyingBelial | Student ID: 1234567
# Module: UFCF8S-30-2 Advanced Software Development

"""
models/cinema.py — Cinema domain model.
"""

from database.db_manager import db


class Cinema:
    def __init__(self, cinemaId: int, name: str, city: str, address: str):
        self.cinemaId = cinemaId
        self.name     = name
        self.city     = city
        self.address  = address

    # ── Factory ───────────────────────────────────────────────────────────────

    @staticmethod
    def from_row(row) -> "Cinema":
        return Cinema(**dict(row))

    @staticmethod
    def get_all():
        rows = db.fetchall("SELECT * FROM cinemas ORDER BY city, name")
        return [Cinema.from_row(r) for r in rows]

    @staticmethod
    def get_by_id(cinema_id: int) -> "Cinema":
        row = db.fetchone("SELECT * FROM cinemas WHERE cinemaId=?", (cinema_id,))
        return Cinema.from_row(row) if row else None

    # ── Domain methods ────────────────────────────────────────────────────────

    def getScreens(self):
        """Return all Screen objects belonging to this cinema."""
        from models.screen import Screen
        rows = db.fetchall(
            "SELECT * FROM screens WHERE cinemaId=? ORDER BY screenNumber",
            (self.cinemaId,),
        )
        return [Screen.from_row(r) for r in rows]

    def getListings(self):
        """Return upcoming listings for this cinema."""
        from models.listing import Listing
        rows = db.fetchall(
            """
            SELECT l.* FROM listings l
            JOIN screens s ON l.screenId = s.screenId
            WHERE s.cinemaId = ? AND l.showDate >= DATE('now')
            ORDER BY l.showDate, l.showTime
            """,
            (self.cinemaId,),
        )
        return [Listing.from_row(r) for r in rows]

    def getPriceBase(self, show_type: str) -> float:
        """Return the base ticket price for the cinema's city and show type."""
        row = db.fetchone(
            "SELECT basePrice FROM pricing_rules WHERE city=? AND showType=?",
            (self.city, show_type),
        )
        return row["basePrice"] if row else 0.0

    def __repr__(self):
        return f"<Cinema id={self.cinemaId} name={self.name!r} city={self.city}>"

