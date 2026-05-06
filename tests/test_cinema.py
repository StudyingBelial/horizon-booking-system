import pytest
from unittest.mock import MagicMock, patch
from models.cinema import Cinema

def test_cinema_init():
    cinema = Cinema(1, "Odeon", "London", "123 Leicester Sq")
    assert cinema.cinemaId == 1
    assert cinema.name == "Odeon"
    assert cinema.city == "London"
    assert cinema.address == "123 Leicester Sq"

def test_cinema_from_row():
    row = {"cinemaId": 1, "name": "Odeon", "city": "London", "address": "123 Leicester Sq"}
    cinema = Cinema.from_row(row)
    assert cinema.name == "Odeon"

@patch("models.cinema.db")
def test_cinema_get_all(mock_db):
    mock_db.fetchall.return_value = [
        {"cinemaId": 1, "name": "C1", "city": "London", "address": "Addr1"},
        {"cinemaId": 2, "name": "C2", "city": "Paris", "address": "Addr2"}
    ]
    cinemas = Cinema.get_all()
    assert len(cinemas) == 2
    assert cinemas[0].name == "C1"
    mock_db.fetchall.assert_called_once()

@patch("models.cinema.db")
def test_cinema_get_by_id(mock_db):
    mock_db.fetchone.return_value = {"cinemaId": 1, "name": "C1", "city": "London", "address": "Addr1"}
    cinema = Cinema.get_by_id(1)
    assert cinema.name == "C1"
    mock_db.fetchone.assert_called_once_with("SELECT * FROM cinemas WHERE cinemaId=?", (1,))

@patch("models.cinema.db")
def test_cinema_get_screens(mock_db):
    # Mocking Screen.from_row is tricky because of the local import
    # But we can mock the db.fetchall call that getScreens uses.
    mock_db.fetchall.return_value = [
        {"screenId": 1, "cinemaId": 1, "screenNumber": 1, "totalCapacity": 150, "lowerHallSeats": 100, "upperGallerySeats": 50}
    ]
    cinema = Cinema(1, "Odeon", "London", "Addr")
    screens = cinema.getScreens()
    assert len(screens) == 1
    assert screens[0].screenId == 1
    mock_db.fetchall.assert_called_once()

@patch("models.cinema.db")
def test_cinema_get_listings(mock_db):
    mock_db.fetchall.return_value = [
        {"listingId": 1, "filmId": 1, "screenId": 1, "showDate": "2026-05-10", "showTime": "14:00", "showType": "2D"}
    ]
    cinema = Cinema(1, "Odeon", "London", "Addr")
    listings = cinema.getListings()
    assert len(listings) == 1
    assert listings[0].listingId == 1
    mock_db.fetchall.assert_called_once()

@patch("models.cinema.db")
def test_cinema_get_price_base(mock_db):
    mock_db.fetchone.return_value = {"basePrice": 12.5}
    cinema = Cinema(1, "Odeon", "London", "Addr")
    price = cinema.getPriceBase("2D")
    assert price == 12.5
    mock_db.fetchone.assert_called_once()

@patch("models.cinema.db")
def test_cinema_get_price_base_not_found(mock_db):
    mock_db.fetchone.return_value = None
    cinema = Cinema(1, "Odeon", "London", "Addr")
    price = cinema.getPriceBase("4D")
    assert price == 0.0

def test_cinema_repr():
    cinema = Cinema(1, "Odeon", "London", "Addr")
    assert repr(cinema) == "<Cinema id=1 name='Odeon' city=London>"
