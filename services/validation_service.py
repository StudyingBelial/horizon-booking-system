# Author: StudyingBelial | Student ID: 1234567
# Module: UFCF8S-30-2 Advanced Software Development

"""
services/validation_service.py — Input and business-rule validation for HCBS.
"""

from datetime import date, timedelta
from config import MAX_ADVANCE_BOOKING_DAYS, MIN_CANCEL_DAYS_BEFORE_SHOW
from utils.helpers import is_valid_email, is_non_empty, parse_date


class ValidationError(Exception):
    """Raised when a business rule or input validation fails."""
    pass


class ValidationService:

    # ── Input validation ──────────────────────────────────────────────────────

    def validate_username(self, username: str) -> None:
        if not is_non_empty(username):
            raise ValidationError("Username cannot be empty.")
        if len(username) < 3:
            raise ValidationError("Username must be at least 3 characters.")

    def validate_password(self, password: str) -> None:
        if not is_non_empty(password):
            raise ValidationError("Password cannot be empty.")
        if len(password) < 6:
            raise ValidationError("Password must be at least 6 characters.")

    def validate_email(self, email: str) -> None:
        if not is_valid_email(email):
            raise ValidationError(f"'{email}' is not a valid email address.")

    def validate_non_empty(self, value: str, field_name: str = "Field") -> None:
        if not is_non_empty(value):
            raise ValidationError(f"{field_name} cannot be empty.")

    # ── Booking business rules ────────────────────────────────────────────────

    def validate_booking_date(self, show_date_str: str) -> None:
        """Show date must be between tomorrow and today + MAX_ADVANCE_BOOKING_DAYS."""
        try:
            show_date = parse_date(show_date_str)
        except ValueError:
            raise ValidationError(f"Invalid date format: {show_date_str!r}. "
                                  f"Expected YYYY-MM-DD.")
        today    = date.today()
        max_date = today + timedelta(days=MAX_ADVANCE_BOOKING_DAYS)

        if show_date <= today:
            raise ValidationError("Show date must be in the future.")
        if show_date > max_date:
            raise ValidationError(
                f"Bookings can only be made up to {MAX_ADVANCE_BOOKING_DAYS} "
                f"days in advance (latest: {max_date})."
            )

    def validate_seats_selected(self, seat_ids: list) -> None:
        if not seat_ids:
            raise ValidationError("At least one seat must be selected.")

    def validate_seat_availability(self, screen, listing_id: int,
                                   seat_ids: list) -> None:
        """Raise if any requested seat is already booked."""
        unavailable = [
            sid for sid in seat_ids
            if not screen.checkSeatAvailability(sid, listing_id)
        ]
        if unavailable:
            raise ValidationError(
                f"The following seats are no longer available: {unavailable}"
            )

    # ── Cancellation business rules ───────────────────────────────────────────

    def validate_cancellation_eligibility(self, booking) -> None:
        """Raise if booking cannot be cancelled."""
        from utils.constants import BookingStatus
        if booking.status == BookingStatus.CANCELLED:
            raise ValidationError("This booking has already been cancelled.")
        if not booking.isEligibleCancel():
            raise ValidationError(
                "Cancellations are only allowed more than "
                f"{MIN_CANCEL_DAYS_BEFORE_SHOW} day(s) before the show date."
            )

    # ── Listing / admin rules ─────────────────────────────────────────────────

    def validate_listing_fields(self, film_id, screen_id,
                                show_date: str, show_time: str,
                                show_type: str) -> None:
        from utils.constants import ShowType
        self.validate_booking_date(show_date)
        if not show_time or len(show_time) != 5:
            raise ValidationError("Show time must be in HH:MM format.")
        valid_types = [st.value for st in ShowType]
        if show_type not in valid_types:
            raise ValidationError(
                f"Show type must be one of: {', '.join(valid_types)}"
            )
        if not film_id or not screen_id:
            raise ValidationError("Film and Screen must be selected.")

