# Author: StudyingBelial | Student ID: 1234567
# Module: UFCF8S-30-2 Advanced Software Development

"""
services/report_service.py — Orchestrates report generation and export.
"""

from models.report import Report


class ReportService:

    REPORT_TYPES = [
        "bookings", "revenue", "cancellations", "occupancy",
        "top_film", "staff_bookings"
    ]

    def generate(self, report_type: str, **kwargs) -> Report:
        if report_type not in self.REPORT_TYPES:
            raise ValueError(
                f"Invalid report type '{report_type}'. "
                f"Choose from: {self.REPORT_TYPES}"
            )
        return Report.generate(report_type, **kwargs)

    def generate_and_export(self, report_type: str, filepath: str = None,
                            **kwargs) -> tuple:
        """
        Generate a report and export it to CSV.
        Returns (Report, filepath_used).
        """
        report   = self.generate(report_type, **kwargs)
        filepath = report.export(filepath)
        return report, filepath

    def get_summary_stats(self) -> dict:
        """Return quick dashboard summary stats for the manager view."""
        from database.db_manager import db
        total_bookings    = db.fetchone(
            "SELECT COUNT(*) as c FROM bookings WHERE status='Confirmed'"
        )["c"]
        total_revenue     = db.fetchone(
            "SELECT COALESCE(SUM(totalCost),0) as s FROM bookings WHERE status='Confirmed'"
        )["s"]
        total_cancel      = db.fetchone(
            "SELECT COUNT(*) as c FROM cancellations"
        )["c"]
        total_refunds     = db.fetchone(
            "SELECT COALESCE(SUM(refundAmount),0) as s FROM cancellations"
        )["s"]
        total_films       = db.fetchone("SELECT COUNT(*) as c FROM films")["c"]
        total_cinemas     = db.fetchone("SELECT COUNT(*) as c FROM cinemas")["c"]
        return {
            "total_bookings": total_bookings,
            "total_revenue":  round(total_revenue, 2),
            "total_cancel":   total_cancel,
            "total_refunds":  round(total_refunds, 2),
            "total_films":    total_films,
            "total_cinemas":  total_cinemas,
        }

