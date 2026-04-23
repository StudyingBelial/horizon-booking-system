# Author: StudyingBelial | Student ID: 1234567
# Module: UFCF8S-30-2 Advanced Software Development

"""
models/report.py — Report domain model.
"""

import csv
import os
from datetime import datetime
from database.db_manager import db
from config import BASE_DIR


class Report:
    """Generates and exports system reports."""

    REPORTS_DIR = os.path.join(BASE_DIR, "reports")

    def __init__(self, report_type: str, data: list, generated_at: str = None):
        self.report_type = report_type
        self.data = data  # list of dicts
        self.generated_at = generated_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ── Factory methods ───────────────────────────────────────────────────────

    @staticmethod
    def generate(report_type: str, **kwargs) -> "Report":
        """Build report data from DB based on report_type."""
        if report_type == "bookings":
            return Report._bookings_report(**kwargs)
        elif report_type == "revenue":
            return Report._revenue_report(**kwargs)
        elif report_type == "cancellations":
            return Report._cancellations_report(**kwargs)
        elif report_type == "occupancy":
            return Report._occupancy_report(**kwargs)
        elif report_type == "top_film":
            return Report._top_film_report(**kwargs)
        elif report_type == "staff_bookings":
            return Report._staff_bookings_report(**kwargs)
        else:
            raise ValueError(f"Unknown report type: {report_type}")

    # ── Report data builders ──────────────────────────────────────────────────

    @staticmethod
    def _bookings_report(**kwargs) -> "Report":
        rows = db.fetchall("""
            SELECT b.bookingRef, f.title as film, l.showDate, l.showTime,
                   l.showType, c.name as cinema, b.numTickets,
                   b.totalCost, b.status, b.bookingDate
            FROM bookings b
            JOIN listings l ON b.listingId = l.listingId
            JOIN films f    ON l.filmId    = f.filmId
            JOIN screens s  ON l.screenId  = s.screenId
            JOIN cinemas c  ON s.cinemaId  = c.cinemaId
            ORDER BY b.bookingDate DESC
            """)
        return Report("bookings", [dict(r) for r in rows])

    @staticmethod
    def _revenue_report(**kwargs) -> "Report":
        month = kwargs.get("month")  # e.g. "2024-05"
        query = """
            SELECT c.city, c.name as cinema, SUM(b.totalCost) as total_revenue,
                   COUNT(b.bookingId) as num_bookings
            FROM bookings b
            JOIN listings l ON b.listingId = l.listingId
            JOIN screens s  ON l.screenId  = s.screenId
            JOIN cinemas c  ON s.cinemaId  = c.cinemaId
            WHERE b.status = 'Confirmed'
        """
        params = []
        if month:
            query += " AND b.bookingDate LIKE ?"
            params.append(f"{month}%")

        query += " GROUP BY c.cinemaId ORDER BY total_revenue DESC"
        rows = db.fetchall(query, tuple(params))
        return Report("revenue", [dict(r) for r in rows])

    @staticmethod
    def _top_film_report(**kwargs) -> "Report":
        month = kwargs.get("month")
        query = """
            SELECT f.title as film, SUM(b.totalCost) as total_revenue,
                   COUNT(b.bookingId) as num_bookings
            FROM bookings b
            JOIN listings l ON b.listingId = l.listingId
            JOIN films f    ON l.filmId    = f.filmId
            WHERE b.status = 'Confirmed'
        """
        params = []
        if month:
            query += " AND b.bookingDate LIKE ?"
            params.append(f"{month}%")

        query += " GROUP BY f.filmId ORDER BY total_revenue DESC"
        rows = db.fetchall(query, tuple(params))
        return Report("top_film", [dict(r) for r in rows])

    @staticmethod
    def _staff_bookings_report(**kwargs) -> "Report":
        month = kwargs.get("month")
        query = """
            SELECT u.username, COUNT(b.bookingId) as num_bookings,
                   SUM(b.totalCost) as total_value
            FROM bookings b
            JOIN users u ON b.staffId = u.userId
            WHERE b.status = 'Confirmed'
        """
        params = []
        if month:
            query += " AND b.bookingDate LIKE ?"
            params.append(f"{month}%")

        query += " GROUP BY u.userId ORDER BY num_bookings DESC"
        rows = db.fetchall(query, tuple(params))
        return Report("staff_bookings", [dict(r) for r in rows])

    @staticmethod
    def _cancellations_report(**kwargs) -> "Report":
        rows = db.fetchall("""
            SELECT cn.bookingRef, cn.cancelDate, cn.refundAmount,
                   b.totalCost, f.title as film, l.showDate
            FROM cancellations cn
            JOIN bookings b ON cn.bookingRef = b.bookingRef
            JOIN listings l ON b.listingId   = l.listingId
            JOIN films f    ON l.filmId      = f.filmId
            ORDER BY cn.cancelDate DESC
            """)
        return Report("cancellations", [dict(r) for r in rows])

    @staticmethod
    def _occupancy_report(**kwargs) -> "Report":
        rows = db.fetchall("""
            SELECT l.listingId, f.title as film, l.showDate, l.showTime,
                   c.name as cinema, s.totalCapacity,
                   COUNT(bs.id) as booked_seats,
                   ROUND(COUNT(bs.id) * 100.0 / s.totalCapacity, 1) as occupancy_pct
            FROM listings l
            JOIN films f         ON l.filmId    = f.filmId
            JOIN screens s       ON l.screenId  = s.screenId
            JOIN cinemas c       ON s.cinemaId  = c.cinemaId
            LEFT JOIN bookings b ON l.listingId = b.listingId AND b.status='Confirmed'
            LEFT JOIN booked_seats bs ON b.bookingId = bs.bookingId
            GROUP BY l.listingId
            ORDER BY l.showDate DESC
            """)
        return Report("occupancy", [dict(r) for r in rows])

    # ── Export ────────────────────────────────────────────────────────────────

    def export(self, filepath: str = None) -> str:
        """Export report data to CSV. Returns the filepath used."""
        os.makedirs(self.REPORTS_DIR, exist_ok=True)
        if filepath is None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{self.report_type}_{ts}.csv"
            filepath = os.path.join(self.REPORTS_DIR, filename)

        if not self.data:
            return filepath

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.data[0].keys())
            writer.writeheader()
            writer.writerows(self.data)

        return filepath

    def __repr__(self):
        return f"<Report type={self.report_type} rows={len(self.data)}>"
