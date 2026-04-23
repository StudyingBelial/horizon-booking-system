# Author: StudyingBelial | Student ID: 1234567
# Module: UFCF8S-30-2 Advanced Software Development

import pytest
from unittest.mock import MagicMock, patch
from models.seat import Seat
from utils.constants import SeatType


def test_seat_init():
    seat = Seat(1, 10, "A1", SeatType.LOWER_HALL)
    assert seat.seatId == 1
    assert seat.screenId == 10
    assert seat.seatNumber == "A1"
    assert seat.seatType == SeatType.LOWER_HALL


def test_seat_from_row():
    row = {
        "seatId": 1,
        "screenId": 10,
        "seatNumber": "A1",
        "seatType": SeatType.LOWER_HALL,
    }
    seat = Seat.from_row(row)
    assert seat.seatId == 1


@patch("models.seat.db")
def test_seat_get_by_id(mock_db):
    mock_db.fetchone.return_value = {
        "seatId": 1,
        "screenId": 10,
        "seatNumber": "A1",
        "seatType": SeatType.LOWER_HALL,
    }
    seat = Seat.get_by_id(1)
    assert seat.seatNumber == "A1"


@patch("models.seat.db")
def test_seat_get_by_screen(mock_db):
    mock_db.fetchall.return_value = [
        {
            "seatId": 1,
            "screenId": 10,
            "seatNumber": "A1",
            "seatType": SeatType.LOWER_HALL,
        },
        {
            "seatId": 2,
            "screenId": 10,
            "seatNumber": "A2",
            "seatType": SeatType.LOWER_HALL,
        },
    ]
    seats = Seat.get_by_screen(10)
    assert len(seats) == 2


@pytest.mark.parametrize(
    "seat_type, base_price, expected",
    [
        (SeatType.LOWER_HALL, 10.0, 10.0),
        (SeatType.UPPER_GALLERY, 10.0, 12.0),  # Assuming UPPER_GALLERY_PREMIUM = 1.2
        (SeatType.VIP, 10.0, 14.4),  # Assuming VIP_PREMIUM = 1.44 (1.2 * 1.2)
    ],
)
def test_seat_calc_price(seat_type, base_price, expected):
    # We need to make sure config values are what we expect or mock them
    # Based on the docstring: Upper Gallery (1.2), VIP (1.2 * 1.2 = 1.44)
    seat = Seat(1, 1, "A1", seat_type)
    assert seat.calcPrice(base_price) == expected


def test_seat_properties():
    vip = Seat(1, 1, "V1", SeatType.VIP)
    assert vip.isVIP() is True
    assert vip.isUpper() is False

    upper = Seat(2, 1, "U1", SeatType.UPPER_GALLERY)
    assert upper.isVIP() is False
    assert upper.isUpper() is True


def test_seat_repr():
    seat = Seat(1, 1, "A1", SeatType.LOWER_HALL)
    assert repr(seat) == f"<Seat id=1 number=A1 type={SeatType.LOWER_HALL}>"
