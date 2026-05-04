"""
hcbs/db.py
----------
Thin database access layer. All raw SQL lives here.
Models and controllers call these functions — never write SQL elsewhere.
"""

import sqlite3
import os
import re
import uuid
from contextlib import contextmanager
from datetime import date, datetime
from typing import Optional, List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "hcbs.db")


@contextmanager
def get_connection():
    """
    Yield a SQLite connection that commits on clean exit, rolls back on
    exception, and always closes — regardless of which database is in use.

    Usage:
        with get_connection() as conn:
            conn.execute(...)
        # committed and closed here
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ── Authentication ──────────────────────────────────────────

def get_user_by_username(username: str) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            "SELECT user_id, username, password_hash, email, role, is_active FROM users WHERE username = ? AND is_active = 1",
            (username,)
        ).fetchone()


def add_user(username: str, password_hash: str, email: str, role: str) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO users (username, password_hash, email, role) VALUES (?, ?, ?, ?)",
            (username, password_hash, email, role)
        )
        return cur.lastrowid


def add_admin(user_id: int):
    with get_connection() as conn:
        conn.execute("INSERT INTO admins (admin_id) VALUES (?)", (user_id,))


def add_manager(user_id: int):
    with get_connection() as conn:
        conn.execute("INSERT INTO managers (manager_id) VALUES (?)", (user_id,))


def add_booking_staff(user_id: int, cinema_id: int):
    with get_connection() as conn:
        conn.execute("INSERT INTO booking_staff (staff_id, cinema_id) VALUES (?, ?)", (user_id, cinema_id))


def deactivate_user(user_id: int):
    with get_connection() as conn:
        conn.execute("UPDATE users SET is_active = 0 WHERE user_id = ?", (user_id,))


# ── Cinemas & Cities ─────────────────────────────────────────

def get_all_cinemas():
    with get_connection() as conn:
        return conn.execute(
            """SELECT c.cinema_id, c.name, c.address, ci.name AS city
            FROM cinemas c JOIN cities ci ON c.city_id = ci.city_id
            ORDER BY ci.name, c.name"""
        ).fetchall()


def get_cinema_by_id(cinema_id: int):
    with get_connection() as conn:
        return conn.execute(
            """SELECT c.*, ci.name AS city
            FROM cinemas c JOIN cities ci ON c.city_id = ci.city_id
            WHERE c.cinema_id = ?""",
            (cinema_id,)
        ).fetchone()


def get_all_cities():
    with get_connection() as conn:
        return conn.execute("SELECT * FROM cities ORDER BY name").fetchall()


def add_city(name: str) -> int:
    with get_connection() as conn:
        cur = conn.execute("INSERT INTO cities (name) VALUES (?)", (name,))
        return cur.lastrowid


def add_cinema(name: str, city_id: int, address: str) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO cinemas (name, city_id, address) VALUES (?,?,?)",
            (name, city_id, address)
        )
        return cur.lastrowid


# ── Screens & Seats ──────────────────────────────────────────

def get_screens_for_cinema(cinema_id: int):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM screens WHERE cinema_id = ? ORDER BY screen_number",
            (cinema_id,)
        ).fetchall()


def get_screen_by_id(screen_id: int):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM screens WHERE screen_id = ?", (screen_id,)
        ).fetchone()


def add_screen(cinema_id: int, screen_number: int, total_capacity: int, lower_hall_seats: int, upper_gallery_seats: int, vip_seats: int = 0) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO screens (cinema_id, screen_number, total_capacity, lower_hall_seats, upper_gallery_seats, vip_seats)
            VALUES (?,?,?,?,?,?)""",
            (cinema_id, screen_number, total_capacity, lower_hall_seats, upper_gallery_seats, vip_seats)
        )
        return cur.lastrowid


def add_seats_bulk(screen_id: int, seats: list) -> None:
    """
    Insert multiple seats for a screen in a single transaction.

    seats: list of (seat_number, seat_type) tuples, e.g.
        [("A1", "lower_hall"), ("A2", "lower_hall"), ("B1", "vip")]
    """
    rows = [(screen_id, seat_number, seat_type) for seat_number, seat_type in seats]
    with get_connection() as conn:
        conn.executemany(
            "INSERT INTO seats (screen_id, seat_number, seat_type) VALUES (?,?,?)",
            rows
        )


def get_seats_for_screen(screen_id: int, seat_type: Optional[str] = None):
    with get_connection() as conn:
        if seat_type:
            return conn.execute(
                "SELECT * FROM seats WHERE screen_id = ? AND seat_type = ? ORDER BY seat_number",
                (screen_id, seat_type)
            ).fetchall()
        return conn.execute(
            "SELECT * FROM seats WHERE screen_id = ? ORDER BY seat_type, seat_number",
            (screen_id,)
        ).fetchall()


def get_booked_seat_ids_for_listing(listing_id: int):
    """Return set of seat_ids already booked for a listing."""
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT bs.seat_id FROM booked_seats bs
            JOIN bookings b ON bs.booking_id = b.booking_id
            WHERE b.listing_id = ? AND b.status = 'confirmed'""",
            (listing_id,)
        ).fetchall()
    return {row["seat_id"] for row in rows}


# ── Films ────────────────────────────────────────────────────

def get_all_films():
    with get_connection() as conn:
        return conn.execute("SELECT * FROM films ORDER BY title").fetchall()


def get_film_by_id(film_id: int):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM films WHERE film_id = ?", (film_id,)).fetchone()


def add_film(title, description, genre, age_rating, duration_mins, actors) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO films (title, description, genre, age_rating, duration_mins, actors)
            VALUES (?,?,?,?,?,?)""",
            (title, description, genre, age_rating, duration_mins, actors)
        )
        return cur.lastrowid


def update_film(film_id: int, **kwargs):
    if not kwargs:
        return
    allowed_keys = {'title', 'description', 'genre', 'age_rating', 'duration_mins', 'actors'}
    unknown = set(kwargs) - allowed_keys
    if unknown:
        raise ValueError(f"Unknown film fields: {unknown}")
    updates, params = zip(*[(f"{k} = ?", v) for k, v in kwargs.items()])
    query = "UPDATE films SET " + ", ".join(updates) + " WHERE film_id = ?"
    with get_connection() as conn:
        conn.execute(query, (*params, film_id))


# ── Listings ─────────────────────────────────────────────────

def get_listings_for_cinema(cinema_id: int, show_date: Optional[str] = None, upcoming_only: bool = False):
    with get_connection() as conn:
        query = """
            SELECT l.*, f.title, f.genre, f.age_rating, f.duration_mins,
                s.screen_number, c.name AS cinema_name, ci.name AS city
            FROM listings l
            JOIN films f   ON l.film_id   = f.film_id
            JOIN screens s ON l.screen_id = s.screen_id
            JOIN cinemas c ON s.cinema_id = c.cinema_id
            JOIN cities ci ON c.city_id   = ci.city_id
            WHERE s.cinema_id = ? AND l.is_active = 1
        """
        params = [cinema_id]
        if show_date:
            query += " AND l.show_date = ?"
            params.append(show_date)
        elif upcoming_only:
            query += " AND l.show_date >= date('now')"

        query += " ORDER BY l.show_date, l.show_time"
        return conn.execute(query, params).fetchall()


def get_listing_by_id(listing_id: int):
    with get_connection() as conn:
        return conn.execute(
            """SELECT l.*, f.title, f.genre, f.age_rating,
                    s.screen_number, s.cinema_id,
                    c.name AS cinema_name, ci.name AS city, ci.city_id
            FROM listings l
            JOIN films f   ON l.film_id   = f.film_id
            JOIN screens s ON l.screen_id = s.screen_id
            JOIN cinemas c ON s.cinema_id = c.cinema_id
            JOIN cities ci ON c.city_id   = ci.city_id
            WHERE l.listing_id = ?""",
            (listing_id,)
        ).fetchone()


def add_listing(film_id, screen_id, show_date, show_time, show_type, created_by) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO listings (film_id, screen_id, show_date, show_time, show_type, created_by)
            VALUES (?,?,?,?,?,?)""",
            (film_id, screen_id, show_date, show_time, show_type, created_by)
        )
        return cur.lastrowid


def update_listing(listing_id: int, **kwargs):
    """
    Update listing fields dynamically.
    Supported keys: film_id, screen_id, show_date, show_time, show_type, is_active
    Raises ValueError for any unrecognised key so typos fail loudly.
    """
    if not kwargs:
        return

    allowed_keys = {'film_id', 'screen_id', 'show_date', 'show_time', 'show_type', 'is_active'}

    unknown = set(kwargs) - allowed_keys
    if unknown:
        raise ValueError(f"Unknown listing fields: {unknown}")

    updates, params = zip(*[(f"{k} = ?", v) for k, v in kwargs.items()])
    query = "UPDATE listings SET " + ", ".join(updates) + " WHERE listing_id = ?"

    with get_connection() as conn:
        conn.execute(query, (*params, listing_id))


def deactivate_listing(listing_id):
    with get_connection() as conn:
        conn.execute(
            "UPDATE listings SET is_active = 0 WHERE listing_id = ?", (listing_id,)
        )


# ── Pricing ──────────────────────────────────────────────────

def get_pricing_rule(city_id: int, show_type: str):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM pricing_rules WHERE city_id = ? AND show_type = ?",
            (city_id, show_type)
        ).fetchone()


def update_pricing_rule(pricing_id: int, **kwargs):
    if not kwargs:
        return
    allowed_keys = {'base_price', 'upper_premium', 'vip_premium'}
    unknown = set(kwargs) - allowed_keys
    if unknown:
        raise ValueError(f"Unknown pricing fields: {unknown}")
    updates, params = zip(*[(f"{k} = ?", v) for k, v in kwargs.items()])
    query = "UPDATE pricing_rules SET " + ", ".join(updates) + " WHERE pricing_id = ?"
    with get_connection() as conn:
        conn.execute(query, (*params, pricing_id))


# ── Bookings ─────────────────────────────────────────────────

def generate_booking_ref() -> str:
    """Generate a unique booking reference using a UUID fragment to avoid race conditions."""
    return f"HC-{uuid.uuid4().hex[:8].upper()}"


def create_full_booking(
    booking_ref: str,
    listing_id: int,
    staff_id: int,
    num_tickets: int,
    total_cost: float,
    seats: list,
) -> int:
    """
    Insert a booking and all its booked_seats in a single atomic transaction.

    seats: list of (seat_id, ticket_type, price_charged) tuples.

    Raises on any failure and rolls back automatically — no partial booking
    is ever committed to the database.
    """
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO bookings (booking_ref, listing_id, staff_id, num_tickets, total_cost)
            VALUES (?,?,?,?,?)""",
            (booking_ref, listing_id, staff_id, num_tickets, total_cost),
        )
        booking_id = cur.lastrowid
        conn.executemany(
            """INSERT INTO booked_seats (booking_id, seat_id, ticket_type, price_charged)
            VALUES (?,?,?,?)""",
            [(booking_id, seat_id, ticket_type, price) for seat_id, ticket_type, price in seats],
        )
        return booking_id


def get_booking_by_ref(booking_ref: str):
    with get_connection() as conn:
        return conn.execute(
            """SELECT b.*, l.show_date, l.show_time, f.title AS film_title,
                    s.screen_number, c.name AS cinema_name
            FROM bookings b
            JOIN listings l ON b.listing_id = l.listing_id
            JOIN films f    ON l.film_id     = f.film_id
            JOIN screens s  ON l.screen_id   = s.screen_id
            JOIN cinemas c  ON s.cinema_id   = c.cinema_id
            WHERE b.booking_ref = ?""",
            (booking_ref,)
        ).fetchone()


def get_booked_seats_for_booking(booking_id: int):
    with get_connection() as conn:
        return conn.execute(
            """SELECT bs.*, s.seat_number, s.seat_type
            FROM booked_seats bs
            JOIN seats s ON bs.seat_id = s.seat_id
            WHERE bs.booking_id = ?""",
            (booking_id,)
        ).fetchall()


def cancel_booking_with_record(booking_id: int, cancelled_by: int, refund_amount: float, charge_rate: float = 0.5) -> None:
    """
    Mark a booking as cancelled and write the cancellation record atomically.
    Either both writes land or neither does.
    """
    with get_connection() as conn:
        conn.execute(
            "UPDATE bookings SET status = 'cancelled' WHERE booking_id = ?",
            (booking_id,),
        )
        conn.execute(
            """INSERT INTO cancellations (booking_id, cancelled_by, refund_amount, charge_rate)
            VALUES (?,?,?,?)""",
            (booking_id, cancelled_by, refund_amount, charge_rate),
        )


# ── Reports ──────────────────────────────────────────────────

def report_bookings_per_listing(cinema_id: int, limit: int = 20):
    with get_connection() as conn:
        return conn.execute(
            """SELECT f.title, l.show_date, l.show_time,
                    COUNT(b.booking_id) AS total_bookings,
                    SUM(b.num_tickets)  AS total_tickets,
                    SUM(b.total_cost)   AS total_revenue
            FROM listings l
            JOIN films f ON l.film_id = f.film_id
            JOIN screens s ON l.screen_id = s.screen_id
            LEFT JOIN bookings b ON l.listing_id = b.listing_id AND b.status='confirmed'
            WHERE s.cinema_id = ? AND l.is_active = 1
            GROUP BY l.listing_id
            ORDER BY total_revenue DESC
            LIMIT ?""",
            (cinema_id, limit)
        ).fetchall()


def report_monthly_revenue(cinema_id: int, year_month: str):
    """year_month format: 'YYYY-MM'"""
    if not re.match(r'^\d{4}-\d{2}$', year_month):
        raise ValueError("Invalid year_month format. Use 'YYYY-MM'.")

    with get_connection() as conn:
        return conn.execute(
            """SELECT SUM(b.total_cost) AS monthly_revenue,
                    COUNT(b.booking_id) AS total_bookings
            FROM bookings b
            JOIN listings l ON b.listing_id = l.listing_id
            JOIN screens s ON l.screen_id = s.screen_id
            WHERE s.cinema_id = ?
                AND strftime('%Y-%m', b.booking_date) = ?
                AND b.status = 'confirmed'""",
            (cinema_id, year_month)
        ).fetchone()


def report_staff_bookings(cinema_id: int, year_month: str):
    """year_month format: 'YYYY-MM'"""
    if not re.match(r'^\d{4}-\d{2}$', year_month):
        raise ValueError("Invalid year_month format. Use 'YYYY-MM'.")

    with get_connection() as conn:
        return conn.execute(
            """SELECT u.username, COUNT(b.booking_id) AS bookings_made
            FROM bookings b
            JOIN users u ON b.staff_id = u.user_id
            JOIN listings l ON b.listing_id = l.listing_id
            JOIN screens s ON l.screen_id = s.screen_id
            WHERE s.cinema_id = ?
                AND strftime('%Y-%m', b.booking_date) = ?
                AND b.status = 'confirmed'
            GROUP BY u.user_id
            ORDER BY bookings_made DESC""",
            (cinema_id, year_month)
        ).fetchall()


def save_report(report_type: str, generated_by: int, data: str) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO reports (report_type, generated_by, data) VALUES (?, ?, ?)",
            (report_type, generated_by, data)
        )
        return cur.lastrowid


def get_reports():
    with get_connection() as conn:
        return conn.execute("SELECT * FROM reports ORDER BY generated_at DESC").fetchall()