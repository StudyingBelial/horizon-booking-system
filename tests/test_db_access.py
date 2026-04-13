import pytest
import os
import sqlite3
import tempfile
from db import db_access

@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    # Create a temporary directory and file for the database
    db_path = tmp_path / "test_hcbs.db"
    monkeypatch.setattr(db_access, "DB_PATH", str(db_path))
    
    # Initialize the database with schema
    schema_path = os.path.join(os.path.dirname(__file__), "..", "db", "schema.sql")
    with open(schema_path, "r") as f:
        schema_sql = f.read()
    
    with sqlite3.connect(str(db_path)) as conn:
        conn.executescript(schema_sql)
    
    yield
    # No need to manually delete, tmp_path handles it

def test_add_and_get_user():
    user_id = db_access.add_user("testuser", "hash", "test@example.com", "admin")
    assert user_id > 0
    
    user = db_access.get_user_by_username("testuser")
    assert user is not None
    assert user["username"] == "testuser"
    assert user["role"] == "admin"
    assert user["is_active"] == 1

    non_existent = db_access.get_user_by_username("nobody")
    assert non_existent is None

def test_deactivate_user():
    user_id = db_access.add_user("active_user", "hash", "active@example.com", "staff")
    db_access.deactivate_user(user_id)
    
    user = db_access.get_user_by_username("active_user")
    assert user is None # get_user_by_username filters by is_active=1

def test_add_roles():
    user_id = db_access.add_user("manager_user", "hash", "m@example.com", "manager")
    db_access.add_manager(user_id)
    # No error means success for now, as these are simple inserts

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
    
    screens = db_access.get_screens_for_cinema(cinema_id)
    assert len(screens) == 1
    assert screens[0]["screen_number"] == 1

def test_get_all_films():
    db_access.add_film("F1", "...", "...", "...", 100, "...")
    db_access.add_film("F2", "...", "...", "...", 110, "...")
    films = db_access.get_all_films()
    assert len(films) == 2

def test_film_crud():
    film_id = db_access.add_film("Original Title", "Desc", "Action", "PG", 100, "Actors")
    assert film_id > 0
    
    film = db_access.get_film_by_id(film_id)
    assert film["title"] == "Original Title"
    
    db_access.update_film(film_id, title="Updated Title", duration_mins=110)
    
    updated_film = db_access.get_film_by_id(film_id)
    assert updated_film["title"] == "Updated Title"
    assert updated_film["duration_mins"] == 110

def test_listing_crud():
    # Setup
    film_id = db_access.add_film("Movie", "...", "...", "...", 120, "...")
    city_id = db_access.add_city("L City")
    cinema_id = db_access.add_cinema("L Cinema", city_id, "...")
    screen_id = db_access.add_screen(cinema_id, 1, 100, 50, 50)
    user_id = db_access.add_user("admin_u", "h", "a@e.com", "admin")
    
    listing_id = db_access.add_listing(film_id, screen_id, "2026-06-01", "19:00", "Evening", user_id)
    assert listing_id > 0
    
    listing = db_access.get_listing_by_id(listing_id)
    assert listing["show_time"] == "19:00"
    
    db_access.update_listing(listing_id, show_time="20:00", is_active=0)
    updated = db_access.get_listing_by_id(listing_id)
    assert updated["show_time"] == "20:00"
    assert updated["is_active"] == 0

def test_booking_and_cancellation():
    # Setup
    film_id = db_access.add_film("B Movie", "...", "Drama", "U", 90, "...")
    city_id = db_access.add_city("B City")
    cinema_id = db_access.add_cinema("B Cinema", city_id, "...")
    screen_id = db_access.add_screen(cinema_id, 1, 50, 25, 25)
    user_id = db_access.add_user("staff_u", "h", "s@e.com", "staff")
    db_access.add_seats_bulk(screen_id, [("S1", "lower")])
    seat_id = db_access.get_seats_for_screen(screen_id)[0]["seat_id"]
    listing_id = db_access.add_listing(film_id, screen_id, "2026-07-01", "20:00", "Evening", user_id)
    
    # Create booking
    booking_ref = db_access.generate_booking_ref()
    booking_id = db_access.create_full_booking(
        booking_ref, listing_id, user_id, 1, 10.0, [(seat_id, "lower", 10.0)]
    )
    assert booking_id > 0
    
    # Verify seat is booked
    booked_seat_ids = db_access.get_booked_seat_ids_for_listing(listing_id)
    assert seat_id in booked_seat_ids
    
    # Cancel booking
    db_access.cancel_booking_with_record(booking_id, user_id, 5.0)
    
    booking_after = db_access.get_booking_by_ref(booking_ref)
    assert booking_after["status"] == "cancelled"
    
    # Verify reports run
    db_access.report_bookings_per_listing(cinema_id)
    db_access.report_monthly_revenue(cinema_id, "2026-07")
    db_access.report_staff_bookings(cinema_id, "2026-07")

def test_pricing_rules():
    city_id = db_access.get_all_cities()[0]["city_id"] # Use seed data
    rule = db_access.get_pricing_rule(city_id, "Morning")
    assert rule is not None
    
    db_access.update_pricing_rule(rule["pricing_id"], base_price=15.0)
    updated = db_access.get_pricing_rule(city_id, "Morning")
    assert updated["base_price"] == 15.0

def test_reports():
    user_id = db_access.add_user("reporter", "h", "r@e.com", "admin")
    report_id = db_access.save_report("revenue", user_id, '{"revenue": 1000}')
    assert report_id > 0
    
    reports = db_access.get_reports()
    assert len(reports) > 0
    assert reports[0]["report_type"] == "revenue"

def test_report_invalid_format():
    with pytest.raises(ValueError, match="Invalid year_month format"):
        db_access.report_monthly_revenue(1, "2026/05")
