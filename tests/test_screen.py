import pytest
from unittest.mock import MagicMock, patch
from models.screen import Screen


def test_screen_init():
    screen = Screen(1, 10, 5, 150, 100, 50)
    assert screen.screenId == 1
    assert screen.cinemaId == 10
    assert screen.screenNumber == 5
    assert screen.totalCapacity == 150


def test_screen_from_row():
    row = {
        "screenId": 1,
        "cinemaId": 10,
        "screenNumber": 5,
        "totalCapacity": 150,
        "lowerHallSeats": 100,
        "upperGallerySeats": 50,
    }
    screen = Screen.from_row(row)
    assert screen.screenNumber == 5


@patch("models.screen.db")
def test_screen_get_by_id(mock_db):
    mock_db.fetchone.return_value = {
        "screenId": 1,
        "cinemaId": 10,
        "screenNumber": 5,
        "totalCapacity": 150,
        "lowerHallSeats": 100,
        "upperGallerySeats": 50,
    }
    screen = Screen.get_by_id(1)
    assert screen.screenId == 1


@patch("models.screen.db")
def test_screen_get_available_seats(mock_db):
    mock_db.fetchall.return_value = [
        {"seatId": 1, "screenId": 1, "seatNumber": "A1", "seatType": "Lower Hall"},
        {"seatId": 2, "screenId": 1, "seatNumber": "A2", "seatType": "Lower Hall"},
    ]
    screen = Screen(1, 1, 1, 100, 50, 50)
    available = screen.getAvailableSeats(listing_id=101)
    assert len(available) == 2
    assert available[0].seatId == 1
    mock_db.fetchall.assert_called_once()


@patch("models.screen.db")
def test_screen_check_seat_availability(mock_db):
    # Available (count = 0)
    mock_db.fetchone.return_value = {"cnt": 0}
    screen = Screen(1, 1, 1, 100, 50, 50)
    assert screen.checkSeatAvailability(seat_id=1, listing_id=101) is True

    # Not Available (count > 0)
    mock_db.fetchone.return_value = {"cnt": 1}
    assert screen.checkSeatAvailability(seat_id=1, listing_id=101) is False


@patch("models.cinema.Cinema.get_by_id")
def test_screen_get_cinema(mock_get_cinema):
    mock_get_cinema.return_value = MagicMock(cinemaId=10)
    screen = Screen(1, 10, 1, 100, 50, 50)
    cinema = screen.getCinema()
    assert cinema.cinemaId == 10
    mock_get_cinema.assert_called_once_with(10)


def test_screen_repr():
    screen = Screen(1, 10, 5, 150, 100, 50)
    assert repr(screen) == "<Screen id=1 cinemaId=10 number=5>"
