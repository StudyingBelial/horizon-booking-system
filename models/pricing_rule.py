# Author: StudyingBelial | Student ID: 1234567
# Module: UFCF8S-30-2 Advanced Software Development

"""
models/pricing_rule.py — PricingRule domain model.
"""

from database.db_manager import db
from config import UPPER_GALLERY_PREMIUM, VIP_PREMIUM
from utils.constants import SeatType


class PricingRule:
    """
    Stores pricing base per (city, showType) and calculates
    Upper Gallery and VIP premiums.
    """

    upperPremium = UPPER_GALLERY_PREMIUM  # 1.20
    vipPremium   = VIP_PREMIUM            # 1.44

    def __init__(self, ruleId: int, city: str, showType: str, basePrice: float):
        self.ruleId    = ruleId
        self.city      = city
        self.showType  = showType
        self.basePrice = basePrice

    @staticmethod
    def from_row(row) -> "PricingRule":
        return PricingRule(**dict(row))

    @staticmethod
    def get(city: str, show_type: str) -> "PricingRule":
        row = db.fetchone(
            "SELECT * FROM pricing_rules WHERE city=? AND showType=?",
            (city, show_type),
        )
        return PricingRule.from_row(row) if row else None

    @staticmethod
    def get_all():
        rows = db.fetchall("SELECT * FROM pricing_rules ORDER BY city, showType")
        return [PricingRule.from_row(r) for r in rows]

    # ── Pricing methods ───────────────────────────────────────────────────────

    def getPrice(self, seat_type: str) -> float:
        """Return price for the given seat type."""
        if seat_type == SeatType.UPPER_GALLERY:
            return self.calcUpper()
        elif seat_type == SeatType.VIP:
            return self.calcVIP()
        return round(self.basePrice, 2)

    def calcUpper(self) -> float:
        """base × 1.20"""
        return round(self.basePrice * self.upperPremium, 2)

    def calcVIP(self) -> float:
        """base × 1.20 × 1.20"""
        return round(self.basePrice * self.vipPremium, 2)

    def __repr__(self):
        return (f"<PricingRule city={self.city} showType={self.showType} "
                f"base=£{self.basePrice:.2f}>")

