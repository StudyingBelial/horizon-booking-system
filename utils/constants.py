"""
utils/constants.py — Shared enumerations and string constants for HCBS.
"""

from enum import Enum


class Role(str, Enum):
    BOOKING_STAFF = "BookingStaff"
    ADMIN = "Admin"
    MANAGER = "Manager"


class SeatType(str, Enum):
    LOWER_HALL = "Lower"
    UPPER_GALLERY = "Upper"
    VIP = "VIP"


class ShowType(str, Enum):
    STANDARD = "Standard"
    IMAX = "IMAX"
    THREE_D = "3D"
    DIRECTORS = "Directors"


class BookingStatus(str, Enum):
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"


class AgeRating(str, Enum):
    U = "U"
    PG = "PG"
    PG13 = "PG-13"
    R15 = "15"
    R18 = "18"


# Ticket types used in booked_seats
TICKET_TYPES = [SeatType.LOWER_HALL, SeatType.UPPER_GALLERY, SeatType.VIP]
