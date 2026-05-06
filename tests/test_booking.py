# Author: StudyingBelial | Student ID: 1234567
# Module: UFCF8S-30-2 Advanced Software Development

"""
tests/test_booking.py — Unit tests for the booking flow.
"""

import unittest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database.db_manager import db
from database.seed_data  import seed
from controllers.booking_controller import BookingController
from services.validation_service    import ValidationError
from models.listing import Listing
from models.seat    import Seat
from models.booking import Booking


def _get_first_listing_and_seats():
    listing = Listing.get_upcoming()[0]
    seats   = listing.getAvailableSeats()
    return listing, seats


class TestBookingFlow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Use an in-memory DB for tests."""
        db._connection = None
        db._instance._connection = None
        import sqlite3, os
        db._connection = sqlite3.connect(":memory:", check_same_thread=False)
        db._connection.row_factory = sqlite3.Row
        db._connection.execute("PRAGMA foreign_keys = ON")
        db.init_schema()
        seed()
        cls.ctrl = BookingController()

    def test_successful_booking(self):
        """A valid listing + available seats → booking created."""
        listing, seats = _get_first_listing_and_seats()
        self.assertTrue(len(seats) > 0, "Need at least one available seat")
        seat_ids = [seats[0].seatId]
        result   = self.ctrl.create_booking(listing.listingId, seat_ids, staff_id=1)
        self.assertTrue(result["success"])
        self.assertIn("HCB-", result["booking"].bookingRef)
        self.assertIn("HORIZON CINEMAS", result["receipt"])

    def test_booking_no_seats_raises(self):
        """Empty seat list must raise ValidationError."""
        listing, _ = _get_first_listing_and_seats()
        with self.assertRaises(ValidationError):
            self.ctrl.create_booking(listing.listingId, [], staff_id=1)

    def test_double_booking_same_seat_fails(self):
        """Booking the same seat twice for the same listing must fail."""
        listing, seats = _get_first_listing_and_seats()
        self.assertTrue(len(seats) > 0)
        seat_ids = [seats[0].seatId]
        # First booking
        self.ctrl.create_booking(listing.listingId, seat_ids, staff_id=1)
        # Second attempt — seat now taken
        with self.assertRaises(ValidationError):
            self.ctrl.create_booking(listing.listingId, seat_ids, staff_id=1)

    def test_booking_invalid_listing(self):
        """Non-existent listing ID must raise ValidationError."""
        with self.assertRaises(ValidationError):
            self.ctrl.create_booking(99999, [1], staff_id=1)

    def test_receipt_contains_film_name(self):
        """Receipt must include the film title."""
        listing, seats = _get_first_listing_and_seats()
        # pick a fresh seat
        available = listing.getAvailableSeats()
        if not available:
            self.skipTest("No available seats left in test DB")
        result = self.ctrl.create_booking(
            listing.listingId, [available[0].seatId], staff_id=1
        )
        film = listing.getFilm()
        self.assertIn(film.title, result["receipt"])


if __name__ == "__main__":
    unittest.main()

