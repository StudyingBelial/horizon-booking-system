import pytest
from unittest.mock import MagicMock, patch
from models.cancellation import Cancellation

def test_cancellation_init():
    c = Cancellation(1, "REF1", "2026-05-10", 12.5, 0.5)
    assert c.cancellationId == 1
    assert c.bookingRef == "REF1"
    assert c.cancelDate == "2026-05-10"
    assert c.refundAmount == 12.5

@patch("models.cancellation.db")
def test_cancellation_get_by_ref(mock_db):
    mock_db.fetchone.return_value = {"cancellationId": 1, "bookingRef": "REF1", "cancelDate": "2026-05-10", "refundAmount": 12.5, "chargeRate": 0.5}
    c = Cancellation.get_by_ref("REF1")
    assert c.bookingRef == "REF1"

@patch("models.cancellation.db")
def test_cancellation_create(mock_db):
    mock_db.execute.return_value = MagicMock()
    mock_db.last_insert_id.return_value = 10
    
    c = Cancellation.create("REF1", 30.0)
    assert c.cancellationId == 10
    assert c.bookingRef == "REF1"
    assert c.refundAmount == 15.0 # 50% of 30
    mock_db.execute.assert_called_once()

def test_cancellation_calc_refund_static():
    assert Cancellation.calcRefundStatic(100.0) == 50.0 # 50% refund

def test_cancellation_repr():
    c = Cancellation(1, "REF1", "2026-05-10", 12.5, 0.5)
    assert repr(c) == "<Cancellation ref=REF1 refund=£12.50 date=2026-05-10>"
