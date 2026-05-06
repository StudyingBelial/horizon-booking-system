"""
controllers/manager_controller.py — Manager operations: cinemas, cities, staff.
"""

from database.db_manager import db
from models.cinema import Cinema
from services.validation_service import ValidationService, ValidationError
from services.report_service import ReportService
from utils.helpers import hash_password


class ManagerController:

    def __init__(self):
        self._validation = ValidationService()
        self._reports = ReportService()

    # ── Cinemas ───────────────────────────────────────────────────────────────

    def add_cinema(self, name: str, city: str, address: str) -> Cinema:
        """Create a new cinema record."""
        self._validation.validate_non_empty(name, "Cinema name")
        self._validation.validate_non_empty(city, "City")
        self._validation.validate_non_empty(address, "Address")

        cur = db.execute(
            "INSERT INTO cinemas(name, city, address) VALUES (?,?,?)",
            (name.strip(), city.strip(), address.strip()),
        )
        cinema_id = db.last_insert_id(cur)
        return Cinema.get_by_id(cinema_id)

    def add_screen(
        self,
        cinema_id: int,
        screen_number: int,
        total_capacity: int,
        lower_seats: int,
        upper_seats: int,
    ) -> dict:
        """Add a screen to an existing cinema."""
        if not Cinema.get_by_id(cinema_id):
            raise ValidationError(f"Cinema ID {cinema_id} not found.")
        if total_capacity < lower_seats + upper_seats:
            raise ValidationError(
                "Total capacity must be >= Lower Hall + Upper Gallery seats."
            )
        cur = db.execute(
            "INSERT INTO screens(cinemaId, screenNumber, totalCapacity, "
            "lowerHallSeats, upperGallerySeats) VALUES (?,?,?,?,?)",
            (cinema_id, screen_number, total_capacity, lower_seats, upper_seats),
        )
        screen_id = db.last_insert_id(cur)
        # Auto-generate seats for new screen
        self._generate_seats(screen_id, lower_seats, upper_seats)
        return {
            "screenId": screen_id,
            "cinemaId": cinema_id,
            "screenNumber": screen_number,
        }

    def _generate_seats(self, screen_id: int, lower: int, upper: int) -> None:
        """Auto-generate seat rows for a newly added screen."""
        seats = []
        # Lower Hall: rows A–D
        for i in range(lower):
            row = chr(ord("A") + i // 10)
            col = (i % 10) + 1
            seats.append((screen_id, f"{row}{col}", "Lower"))
        # Upper Gallery: rows E–F
        for i in range(upper):
            row = chr(ord("E") + i // 10)
            col = (i % 10) + 1
            seats.append((screen_id, f"{row}{col}", "Upper"))
        # 6 VIP seats always
        for i in range(1, 7):
            seats.append((screen_id, f"VIP-{i:02d}", "VIP"))

        db.executemany(
            "INSERT INTO seats(screenId, seatNumber, seatType) VALUES (?,?,?)",
            seats,
        )

    def add_city(self, city_name: str) -> str:
        """Register a new city by inserting a default Standard pricing rule."""
        self._validation.validate_non_empty(city_name, "City name")
        existing = db.fetchone(
            "SELECT COUNT(*) as c FROM pricing_rules WHERE city=?",
            (city_name.strip(),),
        )
        if existing and existing["c"] > 0:
            raise ValidationError(f"City '{city_name}' already exists.")

        # Insert default pricing for all show types and time slots
        defaults = []
        show_types = ["Standard", "IMAX", "3D", "Directors"]
        slots = ["Morning", "Afternoon", "Evening"]
        for st in show_types:
            for sl in slots:
                defaults.append((city_name, st, sl, 10.00))

        db.executemany(
            "INSERT INTO pricing_rules(city, showType, timeSlot, basePrice) VALUES (?,?,?,?)",
            defaults,
        )
        return city_name

    def get_all_cinemas(self) -> list:
        return Cinema.get_all()

    def get_all_cities(self) -> list:
        rows = db.fetchall("SELECT DISTINCT city FROM pricing_rules ORDER BY city")
        return [r["city"] for r in rows]

    # ── Staff management ──────────────────────────────────────────────────────

    def manage_staff(self, action: str, **kwargs) -> dict:
        """
        action = 'add' | 'remove' | 'list'
        For 'add': username, password, email, role
        For 'remove': user_id
        """
        if action == "add":
            return self._add_user(**kwargs)
        elif action == "remove":
            return self._remove_user(**kwargs)
        elif action == "list":
            return self._list_staff()
        else:
            raise ValidationError(f"Unknown action: {action}")

    def _add_user(self, username: str, password: str, email: str, role: str) -> dict:
        self._validation.validate_username(username)
        self._validation.validate_password(password)
        self._validation.validate_email(email)

        valid_roles = ["BookingStaff", "Admin", "Manager"]
        if role not in valid_roles:
            raise ValidationError(f"Role must be one of: {valid_roles}")

        existing = db.fetchone("SELECT userId FROM users WHERE username=?", (username,))
        if existing:
            raise ValidationError(f"Username '{username}' is already taken.")

        cur = db.execute(
            "INSERT INTO users(username, passwordHash, email, role) VALUES (?,?,?,?)",
            (username, hash_password(password), email, role),
        )
        return {"userId": db.last_insert_id(cur), "username": username, "role": role}

    def _remove_user(self, user_id: int) -> dict:
        row = db.fetchone("SELECT * FROM users WHERE userId=?", (user_id,))
        if not row:
            raise ValidationError(f"User ID {user_id} not found.")
        db.execute("DELETE FROM users WHERE userId=?", (user_id,))
        return {"removed": user_id}

    def _list_staff(self) -> list:
        rows = db.fetchall(
            "SELECT userId, username, email, role FROM users ORDER BY role, username"
        )
        return [dict(r) for r in rows]

    # ── Pricing rules ─────────────────────────────────────────────────────────

    def update_pricing(self, city: str, show_type: str, time_slot: str, base_price: float) -> bool:
        if base_price <= 0:
            raise ValidationError("Base price must be greater than zero.")
        db.execute(
            "UPDATE pricing_rules SET basePrice=? WHERE city=? AND showType=? AND timeSlot=?",
            (base_price, city, show_type, time_slot),
        )
        return True

    # ── Dashboard stats ───────────────────────────────────────────────────────

    def get_summary_stats(self) -> dict:
        return self._reports.get_summary_stats()
