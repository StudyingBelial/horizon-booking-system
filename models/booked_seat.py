"""
models/booked_seat.py — BookedSeat domain model.
"""

from database.db_manager import db


class BookedSeat:
    def __init__(
        self, id: int, bookingId: int, seatId: int, ticketType: str, priceCharged: float
    ):
        self.id = id
        self.bookingId = bookingId
        self.seatId = seatId
        self.ticketType = ticketType
        self.priceCharged = priceCharged

    @staticmethod
    def from_row(row) -> "BookedSeat":
        return BookedSeat(**dict(row))

    @staticmethod
    def get_by_booking(booking_id: int):
        rows = db.fetchall(
            "SELECT * FROM booked_seats WHERE bookingId=?", (booking_id,)
        )
        return [BookedSeat.from_row(r) for r in rows]

    @staticmethod
    def create(
        booking_id: int, seat_id: int, ticket_type: str, price_charged: float
    ) -> "BookedSeat":
        cur = db.execute(
            """
            INSERT INTO booked_seats(bookingId, seatId, ticketType, priceCharged)
            VALUES (?,?,?,?)
            """,
            (booking_id, seat_id, ticket_type, price_charged),
        )
        return BookedSeat(
            id=db.last_insert_id(cur),
            bookingId=booking_id,
            seatId=seat_id,
            ticketType=ticket_type,
            priceCharged=price_charged,
        )

    def getSeat(self):
        from models.seat import Seat

        return Seat.get_by_id(self.seatId)

    def __repr__(self):
        return (
            f"<BookedSeat bookingId={self.bookingId} seatId={self.seatId} "
            f"type={self.ticketType} price=£{self.priceCharged:.2f}>"
        )
