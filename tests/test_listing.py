# Author: StudyingBelial | Student ID: 1234567
# Module: UFCF8S-30-2 Advanced Software Development

import pytest
from unittest.mock import MagicMock, patch
from models.listing import Listing

def test_listing_init():
    listing = Listing(1, 10, 100, "2026-05-10", "14:00", "2D")
    assert listing.listingId == 1
    assert listing.filmId == 10
    assert listing.screenId == 100
    assert listing.showDate == "2026-05-10"
    assert listing.showTime == "14:00"
    assert listing.showType == "2D"

def test_listing_from_row():
    row = {
        "listingId": 1, "filmId": 10, "screenId": 100,
        "showDate": "2026-05-10", "showTime": "14:00", "showType": "2D"
    }
    listing = Listing.from_row(row)
    assert listing.listingId == 1

@patch("models.listing.db")
def test_listing_get_by_id(mock_db):
    mock_db.fetchone.return_value = {
        "listingId": 1, "filmId": 10, "screenId": 100,
        "showDate": "2026-05-10", "showTime": "14:00", "showType": "2D"
    }
    listing = Listing.get_by_id(1)
    assert listing.listingId == 1

@patch("models.listing.db")
def test_listing_get_upcoming(mock_db):
    mock_db.fetchall.return_value = [
        {"listingId": 1, "filmId": 10, "screenId": 100, "showDate": "2026-05-10", "showTime": "14:00", "showType": "2D"}
    ]
    listings = Listing.get_upcoming()
    assert len(listings) == 1
    assert listings[0].listingId == 1

@patch("models.film.Film.get_by_id")
def test_listing_get_film(mock_get_film):
    mock_get_film.return_value = MagicMock(title="Inception")
    listing = Listing(1, 10, 100, "2026-05-10", "14:00", "2D")
    film = listing.getFilm()
    assert film.title == "Inception"
    mock_get_film.assert_called_once_with(10)

@patch("models.screen.Screen.get_by_id")
def test_listing_get_screen(mock_get_screen):
    mock_get_screen.return_value = MagicMock(screenId=100)
    listing = Listing(1, 10, 100, "2026-05-10", "14:00", "2D")
    screen = listing.getScreen()
    assert screen.screenId == 100
    mock_get_screen.assert_called_once_with(100)

@patch("models.listing.Listing.getScreen")
def test_listing_get_available_seats(mock_get_screen):
    mock_screen = MagicMock()
    mock_screen.getAvailableSeats.return_value = [MagicMock(seatId=1)]
    mock_get_screen.return_value = mock_screen
    
    listing = Listing(1, 10, 100, "2026-05-10", "14:00", "2D")
    available = listing.getAvailableSeats()
    assert len(available) == 1
    mock_screen.getAvailableSeats.assert_called_once_with(1)

@patch("models.pricing_rule.PricingRule.get")
@patch("models.listing.Listing.getScreen")
def test_listing_calc_ticket_price(mock_get_screen, mock_rule_get):
    mock_cinema = MagicMock(city="London")
    mock_screen = MagicMock()
    mock_screen.getCinema.return_value = mock_cinema
    mock_get_screen.return_value = mock_screen
    
    mock_rule = MagicMock()
    mock_rule.getPrice.return_value = 15.0
    mock_rule_get.return_value = mock_rule
    
    listing = Listing(1, 10, 100, "2026-05-10", "14:00", "2D")
    price = listing.calcTicketPrice("VIP")
    
    assert price == 15.0
    mock_rule_get.assert_called_once_with("London", "2D")
    mock_rule.getPrice.assert_called_once_with("VIP")

def test_listing_repr():
    listing = Listing(1, 10, 100, "2026-05-10", "14:00", "2D")
    assert repr(listing) == "<Listing id=1 filmId=10 date=2026-05-10 time=14:00>"

