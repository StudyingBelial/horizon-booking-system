"""
models/booking.py — Booking domain model.
"""

from datetime import date
from database.db_manager import db
from utils.helpers import generate_booking_ref, now_str, format_currency
from utils.constants import BookingStatus
from config import MIN_CANCEL_DAYS_BEFORE_SHOW


class Booking:
    def __init__(
        self,
        bookingId: int,
        bookingRef: str,
        listingId: int,
        staffId: int,
        bookingDate: str,
        numTickets: int,
        totalCost: float,
        status: str,
    ):
        self.bookingId = bookingId
        self.bookingRef = bookingRef
        self.listingId = listingId
        self.staffId = staffId
        self.bookingDate = bookingDate
        self.numTickets = numTickets
        self.totalCost = totalCost
        self.status = status

    # ── Factories ─────────────────────────────────────────────────────────────

    @staticmethod
    def from_row(row) -> "Booking":
        return Booking(**dict(row))

    @staticmethod
    def get_by_ref(booking_ref: str) -> "Booking":
        row = db.fetchone("SELECT * FROM bookings WHERE bookingRef=?", (booking_ref,))
        return Booking.from_row(row) if row else None

    @staticmethod
    def get_all():
        rows = db.fetchall("SELECT * FROM bookings ORDER BY bookingDate DESC")
        return [Booking.from_row(r) for r in rows]

    @staticmethod
    def create(
        listing_id: int, staff_id: int, num_tickets: int, total_cost: float
    ) -> "Booking":
        """Persist a new Confirmed booking and return the instance."""
        ref = generate_booking_ref()
        date = now_str()
        cur = db.execute(
            """
            INSERT INTO bookings
              (bookingRef, listingId, staffId, bookingDate, numTickets, totalCost, status)
            VALUES (?,?,?,?,?,?,?)
            """,
            (
                ref,
                listing_id,
                staff_id,
                date,
                num_tickets,
                total_cost,
                BookingStatus.CONFIRMED,
            ),
        )
        return Booking(
            bookingId=db.last_insert_id(cur),
            bookingRef=ref,
            listingId=listing_id,
            staffId=staff_id,
            bookingDate=date,
            numTickets=num_tickets,
            totalCost=total_cost,
            status=BookingStatus.CONFIRMED,
        )

    # ── Domain logic ──────────────────────────────────────────────────────────

    def calcTotal(self, seat_prices: list) -> float:
        """Sum a list of seat prices and store in totalCost."""
        self.totalCost = round(sum(seat_prices), 2)
        return self.totalCost

    def isEligibleCancel(self) -> bool:
        """Cancellation allowed only if showDate is strictly more than 1 day away."""
        from models.listing import Listing

        listing = Listing.get_by_id(self.listingId)
        if not listing:
            return False
        show = date.fromisoformat(listing.showDate)
        delta = (show - date.today()).days
        return (
            self.status == BookingStatus.CONFIRMED
            and delta > MIN_CANCEL_DAYS_BEFORE_SHOW
        )

    def cancel(self) -> bool:
        """Mark booking as Cancelled in the database."""
        if not self.isEligibleCancel():
            return False
        db.execute(
            "UPDATE bookings SET status=? WHERE bookingRef=?",
            (BookingStatus.CANCELLED, self.bookingRef),
        )
        self.status = BookingStatus.CANCELLED
        return True

    def getBookedSeats(self):
        """Return all BookedSeat records for this booking."""
        from models.booked_seat import BookedSeat

        return BookedSeat.get_by_booking(self.bookingId)

    def getListing(self):
        from models.listing import Listing

        return Listing.get_by_id(self.listingId)

    def generateReceipt(self) -> str:
        """Build a human-readable receipt string."""
        listing = self.getListing()
        film = listing.getFilm() if listing else None
        screen = listing.getScreen() if listing else None
        cinema = screen.getCinema() if screen else None
        seats = self.getBookedSeats()

        seat_lines = "\n".join(
            f"  {i+1}. Seat {s.seatId} [{s.ticketType}] – {format_currency(s.priceCharged)}"
            for i, s in enumerate(seats)
        )

        return (
            f"═══════════════════════════════════════\n"
            f"     HORIZON CINEMAS BOOKING RECEIPT\n"
            f"═══════════════════════════════════════\n"
            f"  Ref      : {self.bookingRef}\n"
            f"  Film     : {film.title if film else 'N/A'}\n"
            f"  Cinema   : {cinema.name if cinema else 'N/A'}\n"
            f"  Screen   : {screen.screenNumber if screen else 'N/A'}\n"
            f"  Date     : {listing.showDate if listing else 'N/A'}\n"
            f"  Time     : {listing.showTime if listing else 'N/A'}\n"
            f"  Show Type: {listing.showType if listing else 'N/A'}\n"
            f"  Tickets  : {self.numTickets}\n"
            f"───────────────────────────────────────\n"
            f"  Seats:\n{seat_lines}\n"
            f"───────────────────────────────────────\n"
            f"  TOTAL    : {format_currency(self.totalCost)}\n"
            f"  Status   : {self.status}\n"
            f"═══════════════════════════════════════\n"
        )

    def __repr__(self):
        return (
            f"<Booking ref={self.bookingRef} status={self.status} "
            f"total=£{self.totalCost:.2f}>"
        )
