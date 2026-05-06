import pytest
from unittest.mock import patch, MagicMock
from controllers.booking_controller import BookingController
from services.validation_service import ValidationError


@pytest.fixture
def booking_controller():
    return BookingController()


@patch("models.listing.Listing.get_by_id")
@patch("models.screen.Screen.get_by_id")
@patch("models.seat.Seat.get_by_id")
@patch("models.booking.Booking.create")
@patch("models.booked_seat.BookedSeat.create")
def test_create_booking_success(
    mock_booked_seat,
    mock_booking,
    mock_seat,
    mock_screen,
    mock_listing,
    booking_controller,
):
    mock_listing.return_value = MagicMock(
        showDate="2026-05-10", screenId=1, showType="Standard"
    )
    mock_screen.return_value = MagicMock(cinemaId=1)
    # Mocking Cinema.get_by_id to avoid DB hit for city
    with patch("models.cinema.Cinema.get_by_id") as mock_cinema_get:
        mock_cinema_get.return_value = MagicMock(city="London")
        mock_seat.return_value = MagicMock(seatId=1, seatType="Lower")

        mock_booking_obj = MagicMock(bookingId=100)
        mock_booking_obj.generateReceipt.return_value = "RECEIPT"
        mock_booking.return_value = mock_booking_obj

        # Execute
        result = booking_controller.create_booking(1, [1], 5)

    # Assert
    assert result["success"] is True
    assert result["receipt"] == "RECEIPT"
    mock_booking.assert_called_once()
    mock_booked_seat.assert_called_once()


@patch("models.listing.Listing.get_by_id")
def test_create_booking_listing_not_found(mock_listing, booking_controller):
    mock_listing.return_value = None
    with pytest.raises(ValidationError, match="Listing 1 not found."):
        booking_controller.create_booking(1, [1], 5)


@patch("models.listing.Listing.get_by_id")
def test_create_booking_no_seats(mock_listing, booking_controller):
    mock_listing.return_value = MagicMock(showDate="2026-05-10")
    with pytest.raises(ValidationError, match="At least one seat must be selected."):
        booking_controller.create_booking(1, [], 5)


@patch("models.booking.Booking.get_by_ref")
@patch("models.cancellation.Cancellation.create")
@patch("models.cancellation.Cancellation.calcRefundStatic")
def test_cancel_booking_success(
    mock_refund, mock_cancel_create, mock_booking_get, booking_controller
):
    mock_booking = MagicMock(bookingRef="REF123", totalCost=100.0)
    mock_booking_get.return_value = mock_booking
    mock_refund.return_value = 80.0

    with patch.object(
        booking_controller._validation, "validate_cancellation_eligibility"
    ):
        result = booking_controller.cancel_booking("REF123")

    assert result["success"] is True
    assert result["refund"] == 80.0
    mock_booking.cancel.assert_called_once()
    mock_cancel_create.assert_called_once_with("REF123", 100.0)


@patch("models.booking.Booking.get_by_ref")
def test_cancel_booking_not_found(mock_booking_get, booking_controller):
    mock_booking_get.return_value = None
    with pytest.raises(
        ValidationError, match="No booking found with reference 'REF123'."
    ):
        booking_controller.cancel_booking("REF123")


@patch("models.listing.Listing.get_by_id")
def test_get_available_seats(mock_listing, booking_controller):
    mock_listing_obj = MagicMock()
    mock_listing_obj.getAvailableSeats.return_value = ["Seat1", "Seat2"]
    mock_listing.return_value = mock_listing_obj

    seats = booking_controller.get_available_seats(1)
    assert seats == ["Seat1", "Seat2"]
