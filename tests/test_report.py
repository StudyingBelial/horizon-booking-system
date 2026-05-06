import pytest
import os
import csv
from unittest.mock import MagicMock, patch, mock_open
from models.report import Report

def test_report_init():
    data = [{"a": 1, "b": 2}]
    report = Report("bookings", data)
    assert report.report_type == "bookings"
    assert report.data == data
    assert report.generated_at is not None

@patch("models.report.db")
def test_generate_bookings(mock_db):
    mock_db.fetchall.return_value = [{"bookingRef": "REF1", "film": "Film 1"}]
    report = Report.generate("bookings")
    assert report.report_type == "bookings"
    assert len(report.data) == 1
    assert report.data[0]["bookingRef"] == "REF1"

@patch("models.report.db")
def test_generate_revenue(mock_db):
    mock_db.fetchall.return_value = [{"city": "London", "total_revenue": 100}]
    report = Report.generate("revenue")
    assert report.report_type == "revenue"
    assert report.data[0]["city"] == "London"

@patch("models.report.db")
def test_generate_cancellations(mock_db):
    mock_db.fetchall.return_value = [{"bookingRef": "REF1", "refundAmount": 10}]
    report = Report.generate("cancellations")
    assert report.report_type == "cancellations"

@patch("models.report.db")
def test_generate_occupancy(mock_db):
    mock_db.fetchall.return_value = [{"listingId": 1, "occupancy_pct": 50}]
    report = Report.generate("occupancy")
    assert report.report_type == "occupancy"

def test_generate_invalid_type():
    with pytest.raises(ValueError, match="Unknown report type"):
        Report.generate("invalid")

@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open)
def test_export(mock_file, mock_makedirs):
    data = [{"col1": "val1", "col2": "val2"}]
    report = Report("test", data)
    
    filepath = "fake_path.csv"
    report.export(filepath)
    
    mock_makedirs.assert_called_once()
    mock_file.assert_called_once_with(filepath, "w", newline="", encoding="utf-8")
    
    # Check if writeheader and writerows were called (implicitly via csv.DictWriter)
    # The first write should be the header
    handle = mock_file()
    handle.write.assert_any_call("col1,col2\r\n")
    handle.write.assert_any_call("val1,val2\r\n")

def test_export_no_data(tmp_path):
    # Should just return the path without writing
    report = Report("test", [])
    path = str(tmp_path / "empty.csv")
    result = report.export(path)
    assert result == path
    assert not os.path.exists(path)

def test_repr():
    report = Report("test", [{}, {}])
    assert repr(report) == "<Report type=test rows=2>"
