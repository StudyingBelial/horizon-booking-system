"""
models/user.py — User hierarchy: User (abstract) → BookingStaff, Admin, Manager.
"""

from abc import ABC, abstractmethod
from utils.helpers import verify_password


class User(ABC):
    """Abstract base class representing a system user."""

    def __init__(self, userId: int, username: str, passwordHash: str,
                 email: str, role: str):
        self.userId       = userId
        self.username     = username
        self.passwordHash = passwordHash
        self.email        = email
        self.role         = role

    @abstractmethod
    def login(self) -> bool:
        """Implemented by subclasses or called via auth_controller."""
        pass

    def check_password(self, plain: str) -> bool:
        return verify_password(plain, self.passwordHash)

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.userId} username={self.username}>"

    @staticmethod
    def from_row(row) -> "User":
        """Factory: create the correct subclass from a DB Row."""
        data = dict(row)
        role = data["role"]
        if role == "BookingStaff":
            return BookingStaff(**data)
        elif role == "Admin":
            return Admin(**data)
        elif role == "Manager":
            return Manager(**data)
        else:
            raise ValueError(f"Unknown role: {role}")


class BookingStaff(User):
    """Staff member who can make and cancel bookings on behalf of customers."""

    def login(self) -> bool:
        return True  # Authentication handled by AuthController

    def makeBooking(self, listing_id: int, seat_ids: list, staff_id: int):
        """Delegate to BookingController — kept here to satisfy OO contract."""
        from controllers.booking_controller import BookingController
        return BookingController().create_booking(listing_id, seat_ids, staff_id)

    def cancelBooking(self, booking_ref: str):
        from controllers.booking_controller import BookingController
        return BookingController().cancel_booking(booking_ref)


class Admin(User):
    """Admin user who manages listings and generates reports."""

    def login(self) -> bool:
        return True

    def addListing(self, film_id, screen_id, show_date, show_time, show_type):
        from controllers.admin_controller import AdminController
        return AdminController().add_listing(film_id, screen_id, show_date,
                                             show_time, show_type)

    def updateListing(self, listing_id, **kwargs):
        from controllers.admin_controller import AdminController
        return AdminController().update_listing(listing_id, **kwargs)

    def removeListing(self, listing_id):
        from controllers.admin_controller import AdminController
        return AdminController().remove_listing(listing_id)

    def generateReport(self, report_type: str, **kwargs):
        from controllers.admin_controller import AdminController
        return AdminController().generate_report(report_type, **kwargs)

    def bookForCustomer(self, listing_id, seat_ids, staff_id):
        from controllers.booking_controller import BookingController
        return BookingController().create_booking(listing_id, seat_ids, staff_id)


class Manager(User):
    """Manager user who configures cinemas and oversees admin features."""

    def login(self) -> bool:
        return True

    def addCinema(self, name, city, address):
        from controllers.manager_controller import ManagerController
        return ManagerController().add_cinema(name, city, address)

    def addCity(self, city_name):
        from controllers.manager_controller import ManagerController
        return ManagerController().add_city(city_name)

    def manageStaff(self, action, **kwargs):
        from controllers.manager_controller import ManagerController
        return ManagerController().manage_staff(action, **kwargs)

    def accessAdminView(self):
        """Managers inherit full admin capabilities."""
        return True
