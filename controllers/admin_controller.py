"""
controllers/admin_controller.py — Admin operations: manage listings, reports.
"""

from models.listing import Listing
from models.film import Film
from models.screen import Screen
from models.cinema import Cinema
from database.db_manager import db
from services.validation_service import ValidationService, ValidationError
from services.report_service import ReportService


class AdminController:

    def __init__(self):
        self._validation = ValidationService()
        self._reports = ReportService()

    # ── Listings ──────────────────────────────────────────────────────────────

    def add_listing(
        self,
        film_id: int,
        screen_id: int,
        show_date: str,
        show_time: str,
        show_type: str,
    ) -> Listing:
        """Validate inputs then insert a new listing, return the Listing object."""
        self._validation.validate_listing_fields(
            film_id, screen_id, show_date, show_time, show_type
        )
        # Verify film and screen exist
        if not Film.get_by_id(film_id):
            raise ValidationError(f"Film ID {film_id} not found.")
        if not Screen.get_by_id(screen_id):
            raise ValidationError(f"Screen ID {screen_id} not found.")

        cur = db.execute(
            "INSERT INTO listings(filmId, screenId, showDate, showTime, showType) "
            "VALUES (?,?,?,?,?)",
            (film_id, screen_id, show_date, show_time, show_type),
        )
        listing_id = db.last_insert_id(cur)
        return Listing.get_by_id(listing_id)

    def update_listing(self, listing_id: int, **kwargs) -> Listing:
        """
        Update one or more fields of an existing listing.
        Accepted keys: film_id, screen_id, show_date, show_time, show_type
        """
        listing = Listing.get_by_id(listing_id)
        if not listing:
            raise ValidationError(f"Listing ID {listing_id} not found.")

        # Build update fields dynamically
        field_map = {
            "film_id": "filmId",
            "screen_id": "screenId",
            "show_date": "showDate",
            "show_time": "showTime",
            "show_type": "showType",
        }
        sets, values = [], []
        for key, col in field_map.items():
            if key in kwargs:
                sets.append(f"{col}=?")
                values.append(kwargs[key])

        if not sets:
            raise ValidationError("No fields provided to update.")

        values.append(listing_id)
        db.execute(
            f"UPDATE listings SET {', '.join(sets)} WHERE listingId=?", tuple(values)
        )
        return Listing.get_by_id(listing_id)

    def remove_listing(self, listing_id: int) -> bool:
        """Delete a listing. Raises if it has confirmed bookings."""
        row = db.fetchone(
            "SELECT COUNT(*) as c FROM bookings "
            "WHERE listingId=? AND status='Confirmed'",
            (listing_id,),
        )
        if row and row["c"] > 0:
            raise ValidationError(
                "Cannot remove a listing that has active confirmed bookings."
            )
        db.execute("DELETE FROM listings WHERE listingId=?", (listing_id,))
        return True

    def get_all_listings(self) -> list:
        return Listing.get_upcoming()

    def get_all_films(self) -> list:
        return Film.get_all()

    def get_all_screens(self) -> list:
        rows = db.fetchall("""
            SELECT s.screenId, s.screenNumber, s.totalCapacity,
                   c.name as cinemaName, c.city
            FROM screens s
            JOIN cinemas c ON s.cinemaId = c.cinemaId
            ORDER BY c.city, c.name, s.screenNumber
            """)
        return [dict(r) for r in rows]

    def add_film(
        self, title: str, description: str, genre: str, age_rating: str, actors: str
    ) -> int:
        """Insert a new film and return its ID."""
        self._validation.validate_non_empty(title, "Film title")
        cur = db.execute(
            "INSERT INTO films(title, description, genre, ageRating, actors) "
            "VALUES (?,?,?,?,?)",
            (title, description, genre, age_rating, actors),
        )
        return db.last_insert_id(cur)

    # ── Reports ───────────────────────────────────────────────────────────────

    def generate_report(
        self, report_type: str, export: bool = False, filepath: str = None, **kwargs
    ):
        """Generate and optionally export a report."""
        if export:
            report, path = self._reports.generate_and_export(
                report_type, filepath, **kwargs
            )
            return report, path
        return self._reports.generate(report_type, **kwargs)

    def get_summary_stats(self) -> dict:
        return self._reports.get_summary_stats()
