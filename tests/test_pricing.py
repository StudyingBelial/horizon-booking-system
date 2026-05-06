"""
tests/test_pricing.py — Unit tests for pricing rules and calculations.
"""

import unittest
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database.db_manager import db
from database.seed_data import seed
from models.pricing_rule import PricingRule
from models.seat import Seat
from services.pricing_service import PricingService
from config import UPPER_GALLERY_PREMIUM, VIP_PREMIUM


class TestPricingRule(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        import sqlite3

        db._instance._connection = None
        db._connection = sqlite3.connect(":memory:", check_same_thread=False)
        db._connection.row_factory = sqlite3.Row
        db._connection.execute("PRAGMA foreign_keys = ON")
        db.init_schema()
        seed()

    def test_lower_hall_price_equals_base(self):
        rule = PricingRule.get("London", "Standard", "Morning")
        self.assertIsNotNone(rule)
        self.assertAlmostEqual(rule.getPrice("Lower"), rule.basePrice, places=2)

    def test_upper_gallery_premium_20_percent(self):
        rule = PricingRule.get("London", "Standard", "Morning")
        expected = round(rule.basePrice * UPPER_GALLERY_PREMIUM, 2)
        self.assertAlmostEqual(rule.getPrice("Upper"), expected, places=2)

    def test_vip_premium_44_percent(self):
        rule = PricingRule.get("London", "Standard", "Morning")
        expected = round(rule.basePrice * VIP_PREMIUM, 2)
        self.assertAlmostEqual(rule.getPrice("VIP"), expected, places=2)

    def test_vip_equals_upper_times_1_2(self):
        """VIP = base × 1.2 × 1.2 = Upper × 1.2"""
        rule = PricingRule.get("London", "Standard", "Morning")
        upper = rule.calcUpper()
        vip = rule.calcVIP()
        self.assertAlmostEqual(vip, round(upper * 1.20, 2), places=2)

    def test_imax_higher_than_standard(self):
        std = PricingRule.get("London", "Standard", "Morning")
        imax = PricingRule.get("London", "IMAX", "Morning")
        self.assertGreater(imax.basePrice, std.basePrice)

    def test_bristol_cheaper_than_london(self):
        london = PricingRule.get("London", "Standard", "Morning")
        bristol = PricingRule.get("Bristol", "Standard", "Morning")
        self.assertGreater(london.basePrice, bristol.basePrice)

    def test_pricing_service_breakdown(self):
        """PricingService.get_price_breakdown returns all three tiers."""
        svc = PricingService()
        from models.listing import Listing

        listing = Listing.get_upcoming()[0]
        bd = svc.get_price_breakdown(listing.listingId)
        self.assertIn("Lower", bd)
        self.assertIn("Upper", bd)
        self.assertIn("VIP", bd)
        self.assertGreater(bd["VIP"], bd["Upper"])
        self.assertGreater(bd["Upper"], bd["Lower"])

    def test_seat_calc_price_lower(self):
        """A Lower seat must return the base price unchanged."""
        seat = Seat(0, 1, "A1", "Lower")
        base = 12.00
        price = seat.calcPrice(base)
        self.assertAlmostEqual(price, base, places=2)

    def test_seat_calc_price_upper(self):
        seat = Seat(0, 1, "E1", "Upper")
        base = 12.00
        self.assertAlmostEqual(
            seat.calcPrice(base), round(base * UPPER_GALLERY_PREMIUM, 2), places=2
        )

    def test_seat_calc_price_vip(self):
        seat = Seat(0, 1, "VIP-01", "VIP")
        base = 12.00
        self.assertAlmostEqual(
            seat.calcPrice(base), round(base * VIP_PREMIUM, 2), places=2
        )


if __name__ == "__main__":
    unittest.main()
