# Author: StudyingBelial | Student ID: 1234567
# Module: UFCF8S-30-2 Advanced Software Development

import pytest
from unittest.mock import patch, MagicMock
from controllers.manager_controller import ManagerController
from services.validation_service import ValidationError


@pytest.fixture
def manager_controller():
    return ManagerController()


@patch("controllers.manager_controller.db")
@patch("models.cinema.Cinema.get_by_id")
def test_add_cinema_success(mock_cinema_get, mock_db, manager_controller):
    mock_db.last_insert_id.return_value = 1
    mock_cinema_get.return_value = MagicMock(cinemaId=1, name="Grand")

    cinema = manager_controller.add_cinema("Grand", "London", "123 St")

    assert cinema.cinemaId == 1
    mock_db.execute.assert_called_once()


@patch("controllers.manager_controller.db")
@patch("models.cinema.Cinema.get_by_id")
def test_add_screen_success(mock_cinema_get, mock_db, manager_controller):
    mock_cinema_get.return_value = MagicMock()
    mock_db.last_insert_id.return_value = 5

    with patch.object(manager_controller, "_generate_seats") as mock_gen:
        res = manager_controller.add_screen(1, 2, 100, 40, 40)

    assert res["screenId"] == 5
    mock_gen.assert_called_once_with(5, 40, 40)


@patch("controllers.manager_controller.db")
def test_add_city_success(mock_db, manager_controller):
    mock_db.fetchone.return_value = {"c": 0}

    city = manager_controller.add_city("Paris")

    assert city == "Paris"
    assert mock_db.executemany.called


@patch("controllers.manager_controller.db")
def test_add_city_exists(mock_db, manager_controller):
    mock_db.fetchone.return_value = {"c": 1}

    with pytest.raises(ValidationError, match="City 'Paris' already exists."):
        manager_controller.add_city("Paris")


@patch("controllers.manager_controller.db")
@patch("controllers.manager_controller.hash_password")
def test_manage_staff_add(mock_hash, mock_db, manager_controller):
    mock_db.fetchone.return_value = None
    mock_db.last_insert_id.return_value = 10
    mock_hash.return_value = "hashed"

    res = manager_controller.manage_staff(
        "add", username="newuser", password="password123", email="e@e.com", role="Admin"
    )

    assert res["userId"] == 10
    assert res["username"] == "newuser"


@patch("controllers.manager_controller.db")
def test_manage_staff_remove(mock_db, manager_controller):
    mock_db.fetchone.return_value = {"userId": 10}

    res = manager_controller.manage_staff("remove", user_id=10)

    assert res["removed"] == 10
    mock_db.execute.assert_called_with("DELETE FROM users WHERE userId=?", (10,))


@patch("controllers.manager_controller.db")
def test_update_pricing_success(mock_db, manager_controller):
    result = manager_controller.update_pricing("London", "IMAX", 15.5)

    assert result is True
    mock_db.execute.assert_called_once()


def test_update_pricing_invalid(manager_controller):
    with pytest.raises(ValidationError, match="Base price must be greater than zero."):
        manager_controller.update_pricing("London", "IMAX", -1)


@patch("controllers.manager_controller.db")
def test_generate_seats_logic(mock_db, manager_controller):
    # This tests the internal _generate_seats logic indirectly or directly
    manager_controller._generate_seats(1, 10, 10)

    # 10 lower + 10 upper + 6 VIP = 26 seats
    args, kwargs = mock_db.executemany.call_args
    assert len(args[1]) == 26
    # Check first lower seat
    assert args[1][0] == (1, "A1", "Lower")
    # Check first upper seat (starts at E)
    assert args[1][10] == (1, "E1", "Upper")
    # Check first VIP seat
    assert args[1][20] == (1, "VIP-01", "VIP")
