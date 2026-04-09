import pytest
from db import db_access

def test_get_user_by_username():
    user = db_access.get_user_by_username("testuser")
    assert user is not None
    assert user["username"] == "testuser"
    assert user["role"] == "admin"

    non_existent = db_access.get_user_by_username("nobody")
    assert non_existent is None

def test_add_and_get_city():
    city_id = db_access.add_city("Test City")
    assert city_id > 0
    
    cities = db_access.get_all_cities()
    assert any(city["name"] == "Test City" for city in cities)

def test_add_and_get_cinema():
    city_id = db_access.add_city("Cinema City")
    cinema_id = db_access.add_cinema("Grand Cinema", city_id, "123 Test St")
    assert cinema_id > 0
    
    cinema = db_access.get_cinema_by_id(cinema_id)
    assert cinema["name"] == "Grand Cinema"
    assert cinema["city"] == "Cinema City"

def test_screen_and_seats():
    city_id = db_access.add_city("Screen City")
    cinema_id = db_access.add_cinema("Screenplex", city_id, "456 Test St")
    
    screen_id = db_access.add_screen(cinema_id, 1, 100, 50, 40, 10)
    assert screen_id > 0
    
    db_access.add_seats_bulk(screen_id, [("A1", "lower"), ("A2", "lower"), ("V1", "vip")])
    
    seats = db_access.get_seats_for_screen(screen_id)
    assert len(seats) == 3
    
    vip_seats = db_access.get_seats_for_screen(screen_id, seat_type="vip")
    assert len(vip_seats) == 1
    assert vip_seats[0]["seat_number"] == "V1"

def test_film_and_listing():
    film_id = db_access.add_film("Test Movie", "A test movie", "Action", "PG-13", 120, "Actor A, Actor B")
    assert film_id > 0
    
    city_id = db_access.add_city("Listing City")
    cinema_id = db_access.add_cinema("Listing Cinema", city_id, "789 Test St")
    screen_id = db_access.add_screen(cinema_id, 1, 100, 50, 50)
    
    listing_id = db_access.add_listing(film_id, screen_id, "2026-06-01", "19:00", "Evening", 1)
    assert listing_id > 0
    
    listings = db_access.get_listings_for_cinema(cinema_id)
    assert len(listings) == 1
    assert listings[0]["title"] == "Test Movie"

def test_booking_and_cancellation():
    # Setup: film, city, cinema, screen, seat, listing
    film_id = db_access.add_film("Booking Movie", "...", "Drama", "U", 90, "...")
    city_id = db_access.add_city("Booking City")
    cinema_id = db_access.add_cinema("Booking Cinema", city_id, "...")
    screen_id = db_access.add_screen(cinema_id, 1, 50, 25, 25)
    db_access.add_seats_bulk(screen_id, [("S1", "lower")])
    seat_id = db_access.get_seats_for_screen(screen_id)[0]["seat_id"]
    listing_id = db_access.add_listing(film_id, screen_id, "2026-07-01", "20:00", "Evening", 1)
    
    # Create booking
    booking_ref = db_access.generate_booking_ref()
    booking_id = db_access.create_full_booking(
        booking_ref, listing_id, 1, 1, 10.0, [(seat_id, "lower", 10.0)]
    )
    assert booking_id > 0
    
    # Verify booking
    booking = db_access.get_booking_by_ref(booking_ref)
    assert booking["status"] == "confirmed"
    
    booked_seats = db_access.get_booked_seats_for_booking(booking_id)
    assert len(booked_seats) == 1
    assert booked_seats[0]["seat_id"] == seat_id
    
    # Cancel booking
    db_access.cancel_booking_with_record(booking_id, 1, 5.0)
    
    booking_after = db_access.get_booking_by_ref(booking_ref)
    assert booking_after["status"] == "cancelled"

def test_reports():
    # This just ensures the queries run without error
    city_id = db_access.add_city("Report City")
    cinema_id = db_access.add_cinema("Report Cinema", city_id, "...")
    
    # Should not raise exception
    db_access.report_bookings_per_listing(cinema_id)
    db_access.report_monthly_revenue(cinema_id, "2026-05")
    db_access.report_staff_bookings(cinema_id, "2026-05")

def test_report_invalid_format():
    with pytest.raises(ValueError, match="Invalid year_month format"):
        db_access.report_monthly_revenue(1, "2026/05")
