"""
tests/test_cancellation.py — Unit tests for cancellation rules.
"""

import unittest
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database.db_manager import db
from database.seed_data import seed
from controllers.booking_controller import BookingController
from services.validation_service import ValidationError
from models.listing import Listing
from models.booking import Booking
from models.cancellation import Cancellation


class TestCancellationFlow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        import sqlite3

        db._instance._connection = None
        db._connection = sqlite3.connect(":memory:", check_same_thread=False)
        db._connection.row_factory = sqlite3.Row
        db._connection.execute("PRAGMA foreign_keys = ON")
        db.init_schema()
        seed()
        cls.ctrl = BookingController()

    def _make_booking(self) -> Booking:
        """Helper to create a fresh booking for testing."""
        listing = Listing.get_upcoming()[-1]  # Pick the last one (7 days ahead)
        seats = listing.getAvailableSeats()
        if not seats:
            self.skipTest("No available seats")
        result = self.ctrl.create_booking(
            listing.listingId, [seats[0].seatId], staff_id=1
        )
        return result["booking"]

    def test_eligible_cancellation(self):
        """A booking for a show > 1 day away is eligible."""
        booking = self._make_booking()
        # All seeded shows are >= 1 day ahead by design
        self.assertTrue(booking.isEligibleCancel())

    def test_cancellation_refund_amount(self):
        """Refund must equal 50 % of total cost."""
        booking = self._make_booking()
        refund = Cancellation.calcRefundStatic(booking.totalCost)
        self.assertAlmostEqual(refund, booking.totalCost * 0.5, places=2)

    def test_cancel_updates_status(self):
        """Cancelling a booking should set its status to Cancelled."""
        booking = self._make_booking()
        result = self.ctrl.cancel_booking(booking.bookingRef)
        self.assertTrue(result["success"])
        updated = Booking.get_by_ref(booking.bookingRef)
        self.assertEqual(updated.status, "Cancelled")

    def test_double_cancel_raises(self):
        """Cancelling an already-cancelled booking must raise ValidationError."""
        booking = self._make_booking()
        self.ctrl.cancel_booking(booking.bookingRef)
        with self.assertRaises(ValidationError):
            self.ctrl.cancel_booking(booking.bookingRef)

    def test_cancel_nonexistent_ref_raises(self):
        """A bogus booking reference must raise ValidationError."""
        with self.assertRaises(ValidationError):
            self.ctrl.cancel_booking("HCB-ZZZZZZZZ")

    def test_cancellation_record_created(self):
        """A cancellations row must be persisted after cancellation."""
        booking = self._make_booking()
        self.ctrl.cancel_booking(booking.bookingRef)
        record = Cancellation.get_by_ref(booking.bookingRef)
        self.assertIsNotNone(record)
        self.assertAlmostEqual(record.refundAmount, booking.totalCost * 0.5, places=2)


if __name__ == "__main__":
    unittest.main()
