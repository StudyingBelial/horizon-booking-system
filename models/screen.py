"""
models/screen.py — Screen domain model.
"""

from database.db_manager import db


class Screen:
    def __init__(self, screenId: int, cinemaId: int, screenNumber: int,
                 totalCapacity: int, lowerHallSeats: int, upperGallerySeats: int):
        self.screenId          = screenId
        self.cinemaId          = cinemaId
        self.screenNumber      = screenNumber
        self.totalCapacity     = totalCapacity
        self.lowerHallSeats    = lowerHallSeats
        self.upperGallerySeats = upperGallerySeats

    @staticmethod
    def from_row(row) -> "Screen":
        return Screen(**dict(row))

    @staticmethod
    def get_by_id(screen_id: int) -> "Screen":
        row = db.fetchone("SELECT * FROM screens WHERE screenId=?", (screen_id,))
        return Screen.from_row(row) if row else None

    @staticmethod
    def get_by_cinema(cinema_id: int):
        rows = db.fetchall(
            "SELECT * FROM screens WHERE cinemaId=? ORDER BY screenNumber",
            (cinema_id,),
        )
        return [Screen.from_row(r) for r in rows]

    def getAvailableSeats(self, listing_id: int):
        """Return Seat objects not already booked for the given listing."""
        from models.seat import Seat
        rows = db.fetchall(
            """
            SELECT s.* FROM seats s
            WHERE s.screenId = ?
              AND s.seatId NOT IN (
                  SELECT bs.seatId FROM booked_seats bs
                  JOIN bookings b ON bs.bookingId = b.bookingId
                  WHERE b.listingId = ? AND b.status = 'Confirmed'
              )
            ORDER BY s.seatType, s.seatNumber
            """,
            (self.screenId, listing_id),
        )
        return [Seat.from_row(r) for r in rows]

    def checkSeatAvailability(self, seat_id: int, listing_id: int) -> bool:
        """Return True if the given seat is free for this listing."""
        row = db.fetchone(
            """
            SELECT COUNT(*) as cnt FROM booked_seats bs
            JOIN bookings b ON bs.bookingId = b.bookingId
            WHERE bs.seatId = ? AND b.listingId = ? AND b.status = 'Confirmed'
            """,
            (seat_id, listing_id),
        )
        return row["cnt"] == 0

    def getCinema(self):
        from models.cinema import Cinema
        return Cinema.get_by_id(self.cinemaId)

    def __repr__(self):
        return (f"<Screen id={self.screenId} cinemaId={self.cinemaId} "
                f"number={self.screenNumber}>")
