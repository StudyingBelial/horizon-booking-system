"""
database/seed_report_data.py — Simulates historical data for report testing.

Generates past listings, bookings, and cancellations to populate reports
as if the system has been running for several weeks.
"""

import sys
import os
import random
from datetime import date, datetime, timedelta

# Ensure project root is on sys.path for standalone execution
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.db_manager import db
from models.seat import Seat
from services.pricing_service import PricingService
from utils.helpers import generate_booking_ref
from utils.constants import BookingStatus

def seed_reports(days_back=30, force=False):
    """
    Generate historical data for the last X days.
    If bookings already exist, skips unless force=True.
    """
    # Ensure DB is connected
    if not db._connection:
        db.connect()
    
    # Check if we already have significant data
    existing = db.fetchone("SELECT COUNT(*) as c FROM bookings")
    if existing["c"] > 10 and not force:
        print("[SEED-REPORTS] Bookings already exist. Skipping report seeding.")
        print("              Use force=True to override.")
        return

    print(f"[SEED-REPORTS] Simulating historical data for the last {days_back} days...")

    # 1. Fetch required base data from existing seeds
    films = db.fetchall("SELECT filmId FROM films")
    screens = db.fetchall("SELECT screenId FROM screens")
    staff = db.fetchall("SELECT userId FROM users WHERE role='BookingStaff'")
    
    if not films or not screens or not staff:
        print("[SEED-REPORTS] ERROR: Missing base data (films/screens/staff).")
        print("               Please run database/seed_data.py first.")
        return

    pricing_svc = PricingService()
    today = date.today()

    # Counters for the summary
    listings_count = 0
    bookings_count = 0
    tickets_count = 0
    cancellations_count = 0
    
    # 2. Iterate backwards through time
    for day_offset in range(1, days_back + 1):
        target_date = today - timedelta(days=day_offset)
        show_date_str = target_date.strftime("%Y-%m-%d")
        
        # Random number of shows per day (3-6)
        num_shows = random.randint(3, 6)
        
        for _ in range(num_shows):
            # Pick random film, screen, time and type
            film_id = random.choice(films)["filmId"]
            screen_row = random.choice(screens)
            screen_id = screen_row["screenId"]
            
            show_types = ["Standard", "IMAX", "3D", "Directors"]
            show_times = ["11:00", "14:00", "17:00", "20:00", "22:30"]
            
            show_type = random.choice(show_types)
            show_time = random.choice(show_times)
            
            # Create historical Listing
            cur = db.execute(
                "INSERT INTO listings (filmId, screenId, showDate, showTime, showType) VALUES (?,?,?,?,?)",
                (film_id, screen_id, show_date_str, show_time, show_type)
            )
            listing_id = db.last_insert_id(cur)
            listings_count += 1
            
            # 3. Generate random bookings for this listing
            # Most shows should have some attendance (e.g. 5-15 bookings)
            num_bookings = random.randint(5, 15)
            
            # Get all seats for this screen to pick from
            seats = db.fetchall("SELECT seatId, seatType FROM seats WHERE screenId=?", (screen_id,))
            random.shuffle(seats)
            
            for _ in range(num_bookings):
                if not seats:
                    break
                
                staff_member = random.choice(staff)
                staff_id = staff_member["userId"]
                
                # Each booking has 1-4 tickets
                num_tickets = random.randint(1, 4)
                if len(seats) < num_tickets:
                    num_tickets = len(seats)
                
                if num_tickets == 0:
                    break
                
                # Pick seats
                booking_seats = [seats.pop() for _ in range(num_tickets)]
                
                # Calculate prices using the same logic as the app
                base_price = pricing_svc.get_base_price(listing_id)
                total_cost = 0.0
                seat_records = []
                
                for s in booking_seats:
                    # Logic mimics Seat.calcPrice
                    # (Hardcoded here for speed in seeding, but matches models/seat.py)
                    s_type = s["seatType"]
                    price = base_price
                    if s_type == "Upper":
                        price = round(base_price * 1.20, 2)
                    elif s_type == "VIP":
                        price = round(base_price * 1.44, 2)
                    
                    total_cost += price
                    seat_records.append((s["seatId"], s_type, price))
                
                # Create Booking record
                ref = generate_booking_ref()
                # Booking date is roughly 1-3 days before the show
                booking_dt = datetime.combine(target_date, datetime.min.time()) - timedelta(days=random.randint(1, 3), hours=random.randint(1, 12))
                booking_date_str = booking_dt.strftime("%Y-%m-%d %H:%M:%S")
                
                cur = db.execute(
                    """INSERT INTO bookings 
                       (bookingRef, listingId, staffId, bookingDate, numTickets, totalCost, status) 
                       VALUES (?,?,?,?,?,?,?)""",
                    (ref, listing_id, staff_id, booking_date_str, num_tickets, round(total_cost, 2), BookingStatus.CONFIRMED)
                )
                booking_id = db.last_insert_id(cur)
                bookings_count += 1
                
                # Create Booked Seats records
                for s_id, s_type, s_price in seat_records:
                    db.execute(
                        "INSERT INTO booked_seats (bookingId, seatId, ticketType, priceCharged) VALUES (?,?,?,?)",
                        (booking_id, s_id, s_type, s_price)
                    )
                    tickets_count += 1
                
                # 4. Randomly simulate cancellations (approx 8% rate)
                if random.random() < 0.08:
                    db.execute("UPDATE bookings SET status=? WHERE bookingId=?", (BookingStatus.CANCELLED, booking_id))
                    
                    # Cancel date is between booking and show
                    cancel_dt = booking_dt + timedelta(hours=random.randint(1, 24))
                    cancel_date_str = cancel_dt.strftime("%Y-%m-%d %H:%M:%S")
                    refund = round(total_cost * 0.5, 2)
                    
                    db.execute(
                        "INSERT INTO cancellations (bookingRef, cancelDate, refundAmount, chargeRate) VALUES (?,?,?,?)",
                        (ref, cancel_date_str, refund, 0.5)
                    )
                    cancellations_count += 1

    print(f"[SEED-REPORTS] SUCCESS: Generated simulation data.")
    print(f"               - Listings:      {listings_count}")
    print(f"               - Bookings:      {bookings_count}")
    print(f"               - Tickets:       {tickets_count}")
    print(f"               - Cancellations: {cancellations_count}")

if __name__ == "__main__":
    # If run directly, we force seed to ensure the user gets what they asked for
    seed_reports(days_back=45, force=True)
    db.close()
