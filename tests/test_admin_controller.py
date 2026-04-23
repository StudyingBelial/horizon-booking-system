import pytest
from unittest.mock import patch, MagicMock
from controllers.admin_controller import AdminController
from services.validation_service import ValidationError


@pytest.fixture
def admin_controller():
    return AdminController()


@patch("controllers.admin_controller.db")
@patch("models.film.Film.get_by_id")
@patch("models.screen.Screen.get_by_id")
@patch("models.listing.Listing.get_by_id")
def test_add_listing_success(
    mock_listing_get, mock_screen_get, mock_film_get, mock_db, admin_controller
):
    mock_film_get.return_value = MagicMock()
    mock_screen_get.return_value = MagicMock()
    mock_db.last_insert_id.return_value = 1
    mock_listing_get.return_value = MagicMock(listingId=1)

    # Use a date within the next 7 days (current is 2026-05-06)
    listing = admin_controller.add_listing(1, 1, "2026-05-10", "20:00", "Standard")

    assert listing.listingId == 1
    mock_db.execute.assert_called_once()


@patch("models.film.Film.get_by_id")
def test_add_listing_film_not_found(mock_film_get, admin_controller):
    mock_film_get.return_value = None
    with pytest.raises(ValidationError, match="Film ID 1 not found."):
        admin_controller.add_listing(1, 1, "2026-05-10", "20:00", "Standard")


@patch("models.listing.Listing.get_by_id")
@patch("controllers.admin_controller.db")
def test_update_listing_success(mock_db, mock_listing_get, admin_controller):
    mock_listing_get.side_effect = [
        MagicMock(listingId=1),
        MagicMock(listingId=1, showType="3D"),
    ]

    listing = admin_controller.update_listing(1, show_type="3D")

    assert listing.showType == "3D"
    assert (
        "UPDATE listings SET showType=? WHERE listingId=?"
        in mock_db.execute.call_args[0][0]
    )


def test_update_listing_no_fields(admin_controller):
    with patch("models.listing.Listing.get_by_id", return_value=MagicMock()):
        with pytest.raises(ValidationError, match="No fields provided to update."):
            admin_controller.update_listing(1)


@patch("controllers.admin_controller.db")
def test_remove_listing_success(mock_db, admin_controller):
    mock_db.fetchone.return_value = {"c": 0}

    result = admin_controller.remove_listing(1)

    assert result is True
    mock_db.execute.assert_called_with("DELETE FROM listings WHERE listingId=?", (1,))


@patch("controllers.admin_controller.db")
def test_remove_listing_active_bookings(mock_db, admin_controller):
    mock_db.fetchone.return_value = {"c": 5}

    with pytest.raises(
        ValidationError,
        match="Cannot remove a listing that has active confirmed bookings.",
    ):
        admin_controller.remove_listing(1)


@patch("controllers.admin_controller.db")
def test_add_film_success(mock_db, admin_controller):
    mock_db.last_insert_id.return_value = 10

    film_id = admin_controller.add_film("Title", "Desc", "Genre", "PG", "Actors")

    assert film_id == 10
    mock_db.execute.assert_called_once()


@patch.object(AdminController, "__init__", return_value=None)
def test_generate_report(mock_init, admin_controller):
    admin_controller._reports = MagicMock()
    admin_controller._reports.generate_and_export.return_value = (
        {"data": "report"},
        "/path/to/file",
    )

    admin_controller.generate_report("sales", export=True, filepath="test.csv")
    admin_controller._reports.generate_and_export.assert_called_once_with(
        "sales", "test.csv"
    )

    admin_controller.generate_report("occupancy")
    admin_controller._reports.generate.assert_called_once_with("occupancy")
