# Author: StudyingBelial | Student ID: 1234567
# Module: UFCF8S-30-2 Advanced Software Development

"""
models/cancellation.py — Cancellation domain model.
"""

from datetime import date
from database.db_manager import db
from utils.helpers import now_str
from config import CANCELLATION_REFUND_RATE, MIN_CANCEL_DAYS_BEFORE_SHOW


class Cancellation:
    chargeRate = CANCELLATION_REFUND_RATE  # 0.50 — half is kept as charge

    def __init__(self, cancellationId: int, bookingRef: str,
                 cancelDate: str, refundAmount: float, chargeRate: float):
        self.cancellationId = cancellationId
        self.bookingRef     = bookingRef
        self.cancelDate     = cancelDate
        self.refundAmount   = refundAmount
        self.chargeRate     = chargeRate

    # ── Factories ─────────────────────────────────────────────────────────────

    @staticmethod
    def from_row(row) -> "Cancellation":
        return Cancellation(**dict(row))

    @staticmethod
    def get_by_ref(booking_ref: str) -> "Cancellation":
        row = db.fetchone(
            "SELECT * FROM cancellations WHERE bookingRef=?", (booking_ref,)
        )
        return Cancellation.from_row(row) if row else None

    @staticmethod
    def create(booking_ref: str, total_cost: float) -> "Cancellation":
        """Persist a new cancellation record and return it."""
        refund      = Cancellation.calcRefundStatic(total_cost)
        cancel_date = now_str()
        cur = db.execute(
            """
            INSERT INTO cancellations(bookingRef, cancelDate, refundAmount, chargeRate)
            VALUES (?,?,?,?)
            """,
            (booking_ref, cancel_date, refund, Cancellation.chargeRate),
        )
        return Cancellation(
            cancellationId = db.last_insert_id(cur),
            bookingRef     = booking_ref,
            cancelDate     = cancel_date,
            refundAmount   = refund,
            chargeRate     = Cancellation.chargeRate,
        )

    # ── Domain logic ──────────────────────────────────────────────────────────

    def calcRefund(self) -> float:
        """Refund = totalCost × (1 - chargeRate). Stored at creation time."""
        return self.refundAmount

    @staticmethod
    def calcRefundStatic(total_cost: float) -> float:
        return round(total_cost * (1 - Cancellation.chargeRate), 2)

    @staticmethod
    def isEligible(booking) -> bool:
        """
        Cancellation allowed ONLY if showDate > today + MIN_CANCEL_DAYS_BEFORE_SHOW.
        """
        from models.listing import Listing
        listing = Listing.get_by_id(booking.listingId)
        if not listing:
            return False
        show  = date.fromisoformat(listing.showDate)
        delta = (show - date.today()).days
        return delta > MIN_CANCEL_DAYS_BEFORE_SHOW

    def __repr__(self):
        return (f"<Cancellation ref={self.bookingRef} "
                f"refund=£{self.refundAmount:.2f} date={self.cancelDate}>")

