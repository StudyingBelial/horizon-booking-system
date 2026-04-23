# Author: StudyingBelial | Student ID: 1234567
# Module: UFCF8S-30-2 Advanced Software Development

"""
models/listing.py — Listing (show) domain model.
"""

from database.db_manager import db


class Listing:
    def __init__(self, listingId: int, filmId: int, screenId: int,
                 showDate: str, showTime: str, showType: str):
        self.listingId = listingId
        self.filmId    = filmId
        self.screenId  = screenId
        self.showDate  = showDate   # 'YYYY-MM-DD'
        self.showTime  = showTime   # 'HH:MM'
        self.showType  = showType

    @staticmethod
    def from_row(row) -> "Listing":
        return Listing(**dict(row))

    @staticmethod
    def get_by_id(listing_id: int) -> "Listing":
        row = db.fetchone("SELECT * FROM listings WHERE listingId=?", (listing_id,))
        return Listing.from_row(row) if row else None

    @staticmethod
    def get_upcoming():
        """All listings from today onwards."""
        rows = db.fetchall(
            "SELECT * FROM listings WHERE showDate >= DATE('now') "
            "ORDER BY showDate, showTime"
        )
        return [Listing.from_row(r) for r in rows]

    @staticmethod
    def get_by_film(film_id: int):
        rows = db.fetchall(
            "SELECT * FROM listings WHERE filmId=? AND showDate >= DATE('now') "
            "ORDER BY showDate, showTime",
            (film_id,),
        )
        return [Listing.from_row(r) for r in rows]

    @staticmethod
    def get_by_screen(screen_id: int):
        rows = db.fetchall(
            "SELECT * FROM listings WHERE screenId=? AND showDate >= DATE('now') "
            "ORDER BY showDate, showTime",
            (screen_id,),
        )
        return [Listing.from_row(r) for r in rows]

    def getFilm(self):
        from models.film import Film
        return Film.get_by_id(self.filmId)

    def getScreen(self):
        from models.screen import Screen
        return Screen.get_by_id(self.screenId)

    def getAvailableSeats(self):
        """Return free seats for this listing via the Screen model."""
        screen = self.getScreen()
        return screen.getAvailableSeats(self.listingId) if screen else []

    def calcTicketPrice(self, seat_type: str) -> float:
        """Calculate price for a seat type using the city's pricing rule."""
        from models.pricing_rule import PricingRule
        screen = self.getScreen()
        cinema = screen.getCinema() if screen else None
        if not cinema:
            return 0.0
        rule = PricingRule.get(cinema.city, self.showType)
        return rule.getPrice(seat_type) if rule else 0.0

    def __repr__(self):
        return (f"<Listing id={self.listingId} filmId={self.filmId} "
                f"date={self.showDate} time={self.showTime}>")

