"""
controllers/booking_controller.py — Orchestrates the full booking and
cancellation sequence flows.

Flow:
  UI → BookingController → Listing / Screen / Seat / PricingRule
      → Booking.create() → BookedSeat.create() → DB
"""

from models.listing      import Listing
from models.screen       import Screen
from models.seat         import Seat
from models.booking      import Booking
from models.booked_seat  import BookedSeat
from models.cancellation import Cancellation
from services.pricing_service    import PricingService
from services.validation_service import ValidationService, ValidationError


class BookingController:

    def __init__(self):
        self._pricing    = PricingService()
        self._validation = ValidationService()

    # ── Booking creation ──────────────────────────────────────────────────────

    def create_booking(self, listing_id: int, seat_ids: list,
                       staff_id: int) -> dict:
        """
        Full booking sequence:
          1. Validate listing exists and date is within advance window
          2. Validate seats are available (no double booking)
          3. Calculate total price
          4. Persist Booking + BookedSeat records
          5. Return receipt dict

        Returns:
            {"success": True, "booking": Booking, "receipt": str}
        or raises ValidationError.
        """
        # ── Step 1: Validate listing ─────────────────────────────────────────
        listing = Listing.get_by_id(listing_id)
        if not listing:
            raise ValidationError(f"Listing {listing_id} not found.")

        self._validation.validate_booking_date(listing.showDate)
        self._validation.validate_seats_selected(seat_ids)

        # ── Step 2: Check seat availability ──────────────────────────────────
        screen = Screen.get_by_id(listing.screenId)
        if not screen:
            raise ValidationError("Screen not found.")
        self._validation.validate_seat_availability(screen, listing_id, seat_ids)

        # ── Step 3: Calculate prices ──────────────────────────────────────────
        seat_prices = []
        seat_objects = []
        for seat_id in seat_ids:
            seat  = Seat.get_by_id(seat_id)
            if not seat:
                raise ValidationError(f"Seat {seat_id} not found.")
            price = self._pricing.get_seat_price(listing_id, seat_id)
            seat_prices.append((seat, price))
            seat_objects.append(seat)

        total = round(sum(p for _, p in seat_prices), 2)

        # ── Step 4: Persist ───────────────────────────────────────────────────
        booking = Booking.create(
            listing_id  = listing_id,
            staff_id    = staff_id,
            num_tickets = len(seat_ids),
            total_cost  = total,
        )
        for seat, price in seat_prices:
            BookedSeat.create(
                booking_id   = booking.bookingId,
                seat_id      = seat.seatId,
                ticket_type  = seat.seatType,
                price_charged= price,
            )

        # ── Step 5: Return receipt ────────────────────────────────────────────
        return {
            "success": True,
            "booking": booking,
            "receipt": booking.generateReceipt(),
        }

    def get_price_breakdown(self, listing_id: int) -> dict:
        """Return Lower / Upper / VIP prices for a listing (for UI display)."""
        return self._pricing.get_price_breakdown(listing_id)

    def get_available_seats(self, listing_id: int) -> list:
        """Return available Seat objects for a listing."""
        listing = Listing.get_by_id(listing_id)
        if not listing:
            return []
        return listing.getAvailableSeats()

    # ── Cancellation ──────────────────────────────────────────────────────────

    def cancel_booking(self, booking_ref: str) -> dict:
        """
        Cancellation sequence:
          1. Lookup booking
          2. Validate eligibility
          3. Calculate refund
          4. Update booking status
          5. Persist Cancellation record
          6. Return result dict

        Returns:
            {"success": True, "refund": float, "message": str}
        or raises ValidationError.
        """
        booking = Booking.get_by_ref(booking_ref.strip().upper())
        if not booking:
            raise ValidationError(
                f"No booking found with reference '{booking_ref}'."
            )

        self._validation.validate_cancellation_eligibility(booking)

        # Calculate refund before cancelling
        refund = Cancellation.calcRefundStatic(booking.totalCost)

        # Update DB status
        booking.cancel()

        # Persist cancellation record
        Cancellation.create(booking.bookingRef, booking.totalCost)

        return {
            "success": True,
            "booking_ref": booking.bookingRef,
            "refund": refund,
            "message": (
                f"Booking {booking.bookingRef} cancelled successfully.\n"
                f"Refund of £{refund:.2f} will be processed."
            ),
        }

    def lookup_booking(self, booking_ref: str) -> Booking:
        """Return the Booking for the given reference (for UI display)."""
        return Booking.get_by_ref(booking_ref.strip().upper())

    def get_all_bookings(self) -> list:
        return Booking.get_all()
