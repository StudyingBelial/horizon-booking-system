# Author: StudyingBelial | Student ID: 1234567
# Module: UFCF8S-30-2 Advanced Software Development

import pytest
from unittest.mock import MagicMock, patch
from models.booking import Booking
from utils.constants import BookingStatus


def test_booking_init():
    booking = Booking(
        1, "REF1", 10, 100, "2026-05-10", 2, 25.0, BookingStatus.CONFIRMED
    )
    assert booking.bookingId == 1
    assert booking.bookingRef == "REF1"
    assert booking.totalCost == 25.0


def test_booking_from_row():
    row = {
        "bookingId": 1,
        "bookingRef": "REF1",
        "listingId": 10,
        "staffId": 100,
        "bookingDate": "2026-05-10",
        "numTickets": 2,
        "totalCost": 25.0,
        "status": BookingStatus.CONFIRMED,
    }
    booking = Booking.from_row(row)
    assert booking.bookingRef == "REF1"


@patch("models.booking.db")
def test_booking_get_by_ref(mock_db):
    mock_db.fetchone.return_value = {
        "bookingId": 1,
        "bookingRef": "REF1",
        "listingId": 10,
        "staffId": 100,
        "bookingDate": "2026-05-10",
        "numTickets": 2,
        "totalCost": 25.0,
        "status": BookingStatus.CONFIRMED,
    }
    booking = Booking.get_by_ref("REF1")
    assert booking.bookingRef == "REF1"


@patch("models.booking.db")
def test_booking_create(mock_db):
    mock_db.execute.return_value = MagicMock()
    mock_db.last_insert_id.return_value = 50

    booking = Booking.create(
        listing_id=10, staff_id=100, num_tickets=2, total_cost=25.0
    )
    assert booking.bookingId == 50
    assert booking.status == BookingStatus.CONFIRMED
    assert "HCB-" in booking.bookingRef


def test_booking_calc_total():
    booking = Booking(1, "REF1", 10, 100, "2026-05-10", 2, 0.0, BookingStatus.CONFIRMED)
    total = booking.calcTotal([12.5, 12.5])
    assert total == 25.0
    assert booking.totalCost == 25.0


@patch("models.listing.Listing.get_by_id")
def test_booking_is_eligible_cancel(mock_get_listing):
    # Mocking date.today() is a bit messy, let's just mock the listing showDate to be far in the future
    from datetime import date, timedelta

    future_date = (date.today() + timedelta(days=5)).isoformat()
    mock_get_listing.return_value = MagicMock(showDate=future_date)

    booking = Booking(
        1, "REF1", 10, 100, "2026-05-10", 2, 25.0, BookingStatus.CONFIRMED
    )
    assert booking.isEligibleCancel() is True

    # Show is today
    mock_get_listing.return_value = MagicMock(showDate=date.today().isoformat())
    assert booking.isEligibleCancel() is False


@patch("models.booking.db")
def test_booking_cancel(mock_db):
    # Actually let's just use the real eligibility logic with a mock listing
    with patch("models.listing.Listing.get_by_id") as mock_get_listing:
        from datetime import date, timedelta

        future_date = (date.today() + timedelta(days=5)).isoformat()
        mock_get_listing.return_value = MagicMock(showDate=future_date)

        booking = Booking(
            1, "REF1", 10, 100, "2026-05-10", 2, 25.0, BookingStatus.CONFIRMED
        )
        success = booking.cancel()
        assert success is True
        assert booking.status == BookingStatus.CANCELLED
        mock_db.execute.assert_called_once()


@patch("models.booked_seat.BookedSeat.get_by_booking")
def test_booking_get_booked_seats(mock_get_seats):
    mock_get_seats.return_value = [MagicMock(id=1)]
    booking = Booking(
        1, "REF1", 10, 100, "2026-05-10", 2, 25.0, BookingStatus.CONFIRMED
    )
    seats = booking.getBookedSeats()
    assert len(seats) == 1
    mock_get_seats.assert_called_once_with(1)


def test_booking_repr():
    booking = Booking(
        1, "REF1", 10, 100, "2026-05-10", 2, 25.0, BookingStatus.CONFIRMED
    )
    # The actual repr seems to include the Enum class name in this environment
    assert (
        repr(booking)
        == f"<Booking ref=REF1 status={BookingStatus.CONFIRMED} total=£25.00>"
    )
