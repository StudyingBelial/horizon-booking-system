# Author: StudyingBelial | Student ID: 1234567
# Module: UFCF8S-30-2 Advanced Software Development

import pytest
from unittest.mock import patch, MagicMock
from models.user import User, BookingStaff, Admin, Manager


def test_user_from_row_booking_staff():
    row = {
        "userId": 1,
        "username": "staff1",
        "passwordHash": "hash",
        "email": "staff1@example.com",
        "role": "BookingStaff",
    }
    user = User.from_row(row)
    assert isinstance(user, BookingStaff)
    assert user.userId == 1
    assert user.username == "staff1"
    assert user.email == "staff1@example.com"


def test_user_from_row_admin():
    row = {
        "userId": 2,
        "username": "admin1",
        "passwordHash": "hash",
        "email": "admin1@example.com",
        "role": "Admin",
    }
    user = User.from_row(row)
    assert isinstance(user, Admin)


def test_user_from_row_manager():
    row = {
        "userId": 3,
        "username": "mgr1",
        "passwordHash": "hash",
        "email": "mgr1@example.com",
        "role": "Manager",
    }
    user = User.from_row(row)
    assert isinstance(user, Manager)


def test_user_from_row_invalid_role():
    row = {
        "userId": 4,
        "username": "hacker",
        "passwordHash": "hash",
        "email": "hacker@example.com",
        "role": "SuperUser",
    }
    with pytest.raises(ValueError, match="Unknown role: SuperUser"):
        User.from_row(row)


@patch("models.user.verify_password")
def test_user_check_password(mock_verify):
    mock_verify.return_value = True
    row = {
        "userId": 1,
        "username": "staff1",
        "passwordHash": "hash",
        "email": "staff1@example.com",
        "role": "BookingStaff",
    }
    user = User.from_row(row)

    result = user.check_password("plain_text")
    assert result is True
    mock_verify.assert_called_once_with("plain_text", "hash")


def test_user_repr():
    user = BookingStaff(
        userId=10, username="jdoe", passwordHash="h", email="e", role="BookingStaff"
    )
    assert repr(user) == "<BookingStaff id=10 username=jdoe>"


# --- BookingStaff Tests ---


def test_booking_staff_login():
    user = BookingStaff(1, "u", "p", "e", "BookingStaff")
    assert user.login() is True


@patch("controllers.booking_controller.BookingController.create_booking")
def test_booking_staff_make_booking(mock_create):
    mock_create.return_value = {"bookingRef": "REF123"}
    user = BookingStaff(1, "u", "p", "e", "BookingStaff")
    res = user.makeBooking(listing_id=10, seat_ids=[1, 2], staff_id=1)

    assert res == {"bookingRef": "REF123"}
    mock_create.assert_called_once_with(10, [1, 2], 1)


@patch("controllers.booking_controller.BookingController.cancel_booking")
def test_booking_staff_cancel_booking(mock_cancel):
    mock_cancel.return_value = True
    user = BookingStaff(1, "u", "p", "e", "BookingStaff")
    res = user.cancelBooking("REF123")

    assert res is True
    mock_cancel.assert_called_once_with("REF123")


# --- Admin Tests ---


def test_admin_login():
    admin = Admin(2, "a", "p", "e", "Admin")
    assert admin.login() is True


@patch("controllers.admin_controller.AdminController.add_listing")
def test_admin_add_listing(mock_add_listing):
    mock_add_listing.return_value = 100
    admin = Admin(2, "a", "p", "e", "Admin")
    res = admin.addListing(1, 2, "2026-10-10", "20:00", "2D")

    assert res == 100
    mock_add_listing.assert_called_once_with(1, 2, "2026-10-10", "20:00", "2D")


@patch("controllers.admin_controller.AdminController.update_listing")
def test_admin_update_listing(mock_update):
    mock_update.return_value = True
    admin = Admin(2, "a", "p", "e", "Admin")
    res = admin.updateListing(100, film_id=5)

    assert res is True
    mock_update.assert_called_once_with(100, film_id=5)


@patch("controllers.admin_controller.AdminController.remove_listing")
def test_admin_remove_listing(mock_remove):
    mock_remove.return_value = True
    admin = Admin(2, "a", "p", "e", "Admin")
    res = admin.removeListing(100)

    assert res is True
    mock_remove.assert_called_once_with(100)


@patch("controllers.admin_controller.AdminController.generate_report")
def test_admin_generate_report(mock_report):
    mock_report.return_value = [{"id": 1}]
    admin = Admin(2, "a", "p", "e", "Admin")
    res = admin.generateReport("sales")

    assert res == [{"id": 1}]
    mock_report.assert_called_once_with("sales")


@patch("controllers.booking_controller.BookingController.create_booking")
def test_admin_book_for_customer(mock_create):
    mock_create.return_value = {"bookingRef": "ADM_REF"}
    admin = Admin(2, "a", "p", "e", "Admin")
    res = admin.bookForCustomer(10, [1], 2)

    assert res == {"bookingRef": "ADM_REF"}
    mock_create.assert_called_once_with(10, [1], 2)


# --- Manager Tests ---


def test_manager_login():
    mgr = Manager(3, "m", "p", "e", "Manager")
    assert mgr.login() is True
    assert mgr.accessAdminView() is True


@patch("controllers.manager_controller.ManagerController.add_cinema")
def test_manager_add_cinema(mock_add):
    mock_add.return_value = 50
    mgr = Manager(3, "m", "p", "e", "Manager")
    res = mgr.addCinema("Grand", "London", "123 St")

    assert res == 50
    mock_add.assert_called_once_with("Grand", "London", "123 St")


@patch("controllers.manager_controller.ManagerController.add_city")
def test_manager_add_city(mock_add_city):
    mock_add_city.return_value = 5
    mgr = Manager(3, "m", "p", "e", "Manager")
    res = mgr.addCity("Paris")

    assert res == 5
    mock_add_city.assert_called_once_with("Paris")


@patch("controllers.manager_controller.ManagerController.manage_staff")
def test_manager_manage_staff(mock_manage):
    mock_manage.return_value = True
    mgr = Manager(3, "m", "p", "e", "Manager")
    res = mgr.manageStaff("remove", user_id=10)

    assert res is True
    mock_manage.assert_called_once_with("remove", user_id=10)
