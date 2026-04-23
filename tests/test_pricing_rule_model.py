# Author: StudyingBelial | Student ID: 1234567
# Module: UFCF8S-30-2 Advanced Software Development

import pytest
from unittest.mock import MagicMock, patch
from models.pricing_rule import PricingRule
from config import UPPER_GALLERY_PREMIUM, VIP_PREMIUM

def test_pricing_rule_init():
    rule = PricingRule(1, "London", "Standard", 10.0)
    assert rule.city == "London"
    assert rule.showType == "Standard"
    assert rule.basePrice == 10.0

@patch("models.pricing_rule.db")
def test_pricing_rule_get(mock_db):
    mock_db.fetchone.return_value = {"ruleId": 1, "city": "London", "showType": "Standard", "basePrice": 12.0}
    rule = PricingRule.get("London", "Standard")
    assert rule.basePrice == 12.0
    mock_db.fetchone.assert_called_once()

def test_pricing_rule_calc_methods():
    rule = PricingRule(1, "London", "Standard", 10.0)
    assert rule.calcUpper() == round(10.0 * UPPER_GALLERY_PREMIUM, 2)
    assert rule.calcVIP() == round(10.0 * VIP_PREMIUM, 2)

@pytest.mark.parametrize("seat_type, expected_factor", [
    ("Lower", 1.0),
    ("Upper", UPPER_GALLERY_PREMIUM),
    ("VIP", VIP_PREMIUM),
    ("Other", 1.0),
])
def test_pricing_rule_get_price(seat_type, expected_factor):
    base = 10.0
    rule = PricingRule(1, "London", "Standard", base)
    assert rule.getPrice(seat_type) == round(base * expected_factor, 2)

def test_pricing_rule_repr():
    rule = PricingRule(1, "London", "Standard", 10.0)
    assert repr(rule) == "<PricingRule city=London showType=Standard base=£10.00>"

