
import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath("."))

from services.pricing_service import PricingService
from models.listing import Listing
from database.db_manager import db

def test_pricing():
    db.connect()
    svc = PricingService()
    
    # Mock some data if needed, but let's assume seed data exists
    # We'll just test the helper
    print(f"10:00 -> {svc._get_time_slot('10:00')}")
    print(f"14:00 -> {svc._get_time_slot('14:00')}")
    print(f"19:00 -> {svc._get_time_slot('19:00')}")
    print(f"07:00 -> {svc._get_time_slot('07:00')}")
    
    # Test base price calculation logic
    # (requires listings in DB)
    listings = Listing.get_upcoming()
    if listings:
        for l in listings[:5]:
            p = svc.get_price_breakdown(l.listingId)
            print(f"Listing {l.listingId} at {l.showTime} ({l.showType}): {p.get('timeSlot')} -> Base £{p.get('base')}")
    else:
        print("No listings found to test.")

if __name__ == "__main__":
    test_pricing()
