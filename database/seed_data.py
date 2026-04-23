# Author: StudyingBelial | Student ID: 1234567
# Module: UFCF8S-30-2 Advanced Software Development

"""
database/seed_data.py — Populates the database with initial sample data.

Run automatically from main.py when the DB is first created.
"""

from database.db_manager import db
from utils.helpers import hash_password


def seed():
    """Insert seed data only if tables are empty."""

    # ── Pricing Rules ────────────────────────────────────────────────────────
    existing = db.fetchone("SELECT COUNT(*) as c FROM pricing_rules")
    if existing["c"] == 0:
        rules = [
            # (city, showType, basePrice)
            ("London", "Standard", 12.00),
            ("London", "IMAX", 16.00),
            ("London", "3D", 14.00),
            ("London", "Directors", 18.00),
            ("Bristol", "Standard", 10.00),
            ("Bristol", "IMAX", 14.00),
            ("Bristol", "3D", 12.00),
            ("Bristol", "Directors", 15.00),
            ("Cardiff", "Standard", 9.50),
            ("Cardiff", "IMAX", 13.00),
            ("Cardiff", "3D", 11.00),
            ("Cardiff", "Directors", 14.00),
            ("Birmingham", "Standard", 7.00),
            ("Birmingham", "IMAX", 10.00),
            ("Birmingham", "3D", 9.00),
            ("Birmingham", "Directors", 11.00),
        ]
        db.executemany(
            "INSERT INTO pricing_rules(city, showType, basePrice) VALUES (?,?,?)",
            rules,
        )

    # ── Cinemas ──────────────────────────────────────────────────────────────
    existing = db.fetchone("SELECT COUNT(*) as c FROM cinemas")
    if existing["c"] == 0:
        cinemas = [
            ("Horizon West End", "London", "1 Leicester Square, London"),
            ("Horizon Canary Wharf", "London", "25 Churchill Place, London"),
            ("Horizon Cabot", "Bristol", "5 Cabot Circus, Bristol"),
            ("Horizon Cribbs", "Bristol", "Cribbs Causeway, Bristol"),
            ("Horizon Cardiff Bay", "Cardiff", "Mermaid Quay, Cardiff"),
            ("Horizon St David's", "Cardiff", "Bridge St, Cardiff"),
            ("Horizon Bullring", "Birmingham", "Bullring Shopping Centre, Birmingham"),
            ("Horizon Brindley", "Birmingham", "Brindleyplace, Birmingham"),
        ]
        db.executemany(
            "INSERT INTO cinemas(name, city, address) VALUES (?,?,?)", cinemas
        )

    # ── Screens ──────────────────────────────────────────────────────────────
    existing = db.fetchone("SELECT COUNT(*) as c FROM screens")
    if existing["c"] == 0:
        # (cinemaId, screenNumber, totalCapacity, lowerHall, upperGallery)
        screens = [
            (1, 1, 120, 80, 40),
            (1, 2, 80, 60, 20),
            (2, 1, 100, 70, 30),
            (3, 1, 90, 60, 30),
            (4, 1, 90, 60, 30),
            (5, 1, 85, 55, 30),
            (6, 1, 85, 55, 30),
            (7, 1, 110, 70, 40),
            (8, 1, 110, 70, 40),
        ]
        db.executemany(
            "INSERT INTO screens(cinemaId, screenNumber, totalCapacity, "
            "lowerHallSeats, upperGallerySeats) VALUES (?,?,?,?,?)",
            screens,
        )

    # ── Seats ─────────────────────────────────────────────────────────────────
    existing = db.fetchone("SELECT COUNT(*) as c FROM seats")
    if existing["c"] == 0:
        _create_seats_for_all_screens()

    # ── Films ─────────────────────────────────────────────────────────────────
    existing = db.fetchone("SELECT COUNT(*) as c FROM films")
    if existing["c"] == 0:
        films = [
            (
                "Galactic Odyssey",
                "An epic journey across star systems.",
                "Sci-Fi",
                "PG-13",
                "Jane Doe, John Smith",
            ),
            (
                "The Last Ember",
                "A war drama set in 1944 Europe.",
                "Drama",
                "15",
                "Alice Brown, Robert Green",
            ),
            (
                "Laugh Out Loud",
                "A hilarious family comedy.",
                "Comedy",
                "PG",
                "Tom White, Lucy Black",
            ),
            (
                "Shadow Protocol",
                "A gripping spy thriller.",
                "Thriller",
                "15",
                "Chris Stone, Emma Lake",
            ),
            (
                "Roar of the Wild",
                "Documentary about African wildlife.",
                "Documentary",
                "U",
                "David Attenborough Jr.",
            ),
        ]
        db.executemany(
            "INSERT INTO films(title, description, genre, ageRating, actors) "
            "VALUES (?,?,?,?,?)",
            films,
        )

    # ── Listings ──────────────────────────────────────────────────────────────
    existing = db.fetchone("SELECT COUNT(*) as c FROM listings")
    if existing["c"] == 0:
        from datetime import date, timedelta

        today = date.today()
        listings = []
        show_configs = [
            (1, 1, "Standard", "10:00"),
            (1, 1, "IMAX", "13:30"),
            (2, 3, "3D", "16:00"),
            (3, 4, "Standard", "18:30"),
            (4, 5, "Directors", "20:00"),
            (5, 7, "Standard", "11:00"),
        ]
        for days_ahead in range(1, 8):
            show_date = (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
            for filmId, screenId, showType, showTime in show_configs:
                listings.append((filmId, screenId, show_date, showTime, showType))

        db.executemany(
            "INSERT INTO listings(filmId, screenId, showDate, showTime, showType) "
            "VALUES (?,?,?,?,?)",
            listings,
        )

    # ── Users ─────────────────────────────────────────────────────────────────
    existing = db.fetchone("SELECT COUNT(*) as c FROM users")
    if existing["c"] == 0:
        users = [
            ("admin", hash_password("admin123"), "admin@horizon.com", "Admin"),
            ("manager", hash_password("manager123"), "manager@horizon.com", "Manager"),
            ("staff1", hash_password("staff123"), "staff1@horizon.com", "BookingStaff"),
            ("staff2", hash_password("staff456"), "staff2@horizon.com", "BookingStaff"),
        ]
        db.executemany(
            "INSERT INTO users(username, passwordHash, email, role) VALUES (?,?,?,?)",
            users,
        )

    print("[SEED] Database seeded successfully.")


def _create_seats_for_all_screens():
    """Generate seat rows for every screen based on its capacity split."""
    screens = db.fetchall(
        "SELECT screenId, lowerHallSeats, upperGallerySeats FROM screens"
    )
    all_seats = []
    for s in screens:
        screen_id = s["screenId"]
        # Lower Hall: rows A-D (up to 80 seats)
        lower = s["lowerHallSeats"]
        all_seats += _gen_seats(screen_id, "Lower", lower, start_row="A")
        # Upper Gallery: rows E-F
        upper = s["upperGallerySeats"]
        all_seats += _gen_seats(screen_id, "Upper", upper, start_row="E")
        # VIP seats: always 10 (as per spec)
        for i in range(1, 11):
            all_seats.append((screen_id, f"VIP-{i:02d}", "VIP"))

    db.executemany(
        "INSERT INTO seats(screenId, seatNumber, seatType) VALUES (?,?,?)",
        all_seats,
    )


def _gen_seats(screen_id: int, seat_type: str, count: int, start_row: str):
    """Generate (screenId, seatNumber, seatType) tuples."""
    seats = []
    row_ord = ord(start_row)
    per_row = 10
    for i in range(count):
        row = chr(row_ord + i // per_row)
        col = (i % per_row) + 1
        seats.append((screen_id, f"{row}{col}", seat_type))
    return seats
