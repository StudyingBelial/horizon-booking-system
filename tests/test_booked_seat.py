import pytest
from unittest.mock import MagicMock, patch
from models.booked_seat import BookedSeat


def test_booked_seat_init():
    bs = BookedSeat(1, 10, 100, "Adult", 12.5)
    assert bs.id == 1
    assert bs.bookingId == 10
    assert bs.seatId == 100
    assert bs.ticketType == "Adult"
    assert bs.priceCharged == 12.5


def test_booked_seat_from_row():
    row = {
        "id": 1,
        "bookingId": 10,
        "seatId": 100,
        "ticketType": "Adult",
        "priceCharged": 12.5,
    }
    bs = BookedSeat.from_row(row)
    assert bs.id == 1


@patch("models.booked_seat.db")
def test_booked_seat_get_by_booking(mock_db):
    mock_db.fetchall.return_value = [
        {
            "id": 1,
            "bookingId": 10,
            "seatId": 100,
            "ticketType": "Adult",
            "priceCharged": 12.5,
        }
    ]
    seats = BookedSeat.get_by_booking(10)
    assert len(seats) == 1
    assert seats[0].id == 1


@patch("models.booked_seat.db")
def test_booked_seat_create(mock_db):
    mock_db.execute.return_value = MagicMock()
    mock_db.last_insert_id.return_value = 5

    bs = BookedSeat.create(10, 100, "Child", 8.0)
    assert bs.id == 5
    assert bs.bookingId == 10
    assert bs.ticketType == "Child"
    mock_db.execute.assert_called_once()


@patch("models.seat.Seat.get_by_id")
def test_booked_seat_get_seat(mock_get_seat):
    mock_get_seat.return_value = MagicMock(seatId=100)
    bs = BookedSeat(1, 10, 100, "Adult", 12.5)
    seat = bs.getSeat()
    assert seat.seatId == 100
    mock_get_seat.assert_called_once_with(100)


def test_booked_seat_repr():
    bs = BookedSeat(1, 10, 100, "Adult", 12.5)
    assert repr(bs) == "<BookedSeat bookingId=10 seatId=100 type=Adult price=£12.50>"
