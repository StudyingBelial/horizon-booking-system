"""
services/pricing_service.py — Calculates ticket prices for bookings.
"""

from models.listing    import Listing
from models.seat       import Seat
from models.pricing_rule import PricingRule
from models.screen     import Screen
from models.cinema     import Cinema


class PricingService:
    """Centralises all price calculation logic, decoupled from UI and models."""

    def get_base_price(self, listing_id: int) -> float:
        """Return the base price for a listing (city + showType)."""
        listing = Listing.get_by_id(listing_id)
        if not listing:
            return 0.0
        screen = Screen.get_by_id(listing.screenId)
        cinema = Cinema.get_by_id(screen.cinemaId) if screen else None
        if not cinema:
            return 0.0
        rule = PricingRule.get(cinema.city, listing.showType)
        return rule.basePrice if rule else 0.0

    def get_seat_price(self, listing_id: int, seat_id: int) -> float:
        """Return the price for a specific seat in a specific listing."""
        base = self.get_base_price(listing_id)
        seat = Seat.get_by_id(seat_id)
        if not seat:
            return 0.0
        return seat.calcPrice(base)

    def get_price_breakdown(self, listing_id: int) -> dict:
        """
        Return a breakdown dict with Lower / Upper / VIP prices
        for display in the booking UI.
        """
        listing = Listing.get_by_id(listing_id)
        if not listing:
            return {}
        screen = Screen.get_by_id(listing.screenId)
        cinema = Cinema.get_by_id(screen.cinemaId) if screen else None
        if not cinema:
            return {}
        rule = PricingRule.get(cinema.city, listing.showType)
        if not rule:
            return {}
        return {
            "Lower":  rule.getPrice("Lower"),
            "Upper":  rule.getPrice("Upper"),
            "VIP":    rule.getPrice("VIP"),
            "base":   rule.basePrice,
            "city":   cinema.city,
            "showType": listing.showType,
        }

    def calc_total(self, listing_id: int, seat_ids: list) -> float:
        """Sum the prices for a list of seat IDs in a listing."""
        return round(sum(self.get_seat_price(listing_id, sid) for sid in seat_ids), 2)
