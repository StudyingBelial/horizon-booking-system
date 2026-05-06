"""
models/seat.py — Seat domain model.
"""

from database.db_manager import db
from config import UPPER_GALLERY_PREMIUM, VIP_PREMIUM
from utils.constants import SeatType


class Seat:
    def __init__(self, seatId: int, screenId: int, seatNumber: str, seatType: str):
        self.seatId = seatId
        self.screenId = screenId
        self.seatNumber = seatNumber
        self.seatType = seatType

    @staticmethod
    def from_row(row) -> "Seat":
        return Seat(**dict(row))

    @staticmethod
    def get_by_id(seat_id: int) -> "Seat":
        row = db.fetchone("SELECT * FROM seats WHERE seatId=?", (seat_id,))
        return Seat.from_row(row) if row else None

    @staticmethod
    def get_by_screen(screen_id: int):
        rows = db.fetchall(
            "SELECT * FROM seats WHERE screenId=? ORDER BY seatType, seatNumber",
            (screen_id,),
        )
        return [Seat.from_row(r) for r in rows]

    # ── Pricing logic ─────────────────────────────────────────────────────────

    def calcPrice(self, base: float) -> float:
        """
        Apply seat-type premium to a base price.
          Lower Hall  → base
          Upper Gallery → base × 1.20
          VIP         → base × 1.20 × 1.20
        """
        if self.seatType == SeatType.UPPER_GALLERY:
            return round(base * UPPER_GALLERY_PREMIUM, 2)
        elif self.seatType == SeatType.VIP:
            return round(base * VIP_PREMIUM, 2)
        return round(base, 2)

    def isVIP(self) -> bool:
        return self.seatType == SeatType.VIP

    def isUpper(self) -> bool:
        return self.seatType == SeatType.UPPER_GALLERY

    def __repr__(self):
        return f"<Seat id={self.seatId} number={self.seatNumber} type={self.seatType}>"
