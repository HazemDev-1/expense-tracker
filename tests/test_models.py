from datetime import date
from decimal import Decimal

import pytest

from expense_tracker.models import Expense, ValidationError


@pytest.mark.parametrize("raw, expected", [("12.5", "12.50"), (" 3 ", "3.00"), ("0.1", "0.10")])
def test_parse_amount_accepts_valid_numbers(raw, expected):
    assert Expense.parse_amount(raw) == Decimal(expected)


@pytest.mark.parametrize("raw", ["0", "-5", "abc", "", "NaN", "Infinity"])
def test_parse_amount_rejects_bad_input(raw):
    with pytest.raises(ValidationError):
        Expense.parse_amount(raw)


def test_parse_date_defaults_to_today():
    assert Expense.parse_date(None) == date.today()


def test_parse_date_rejects_wrong_format():
    with pytest.raises(ValidationError):
        Expense.parse_date("29/09/2026")


def test_category_is_normalized():
    assert Expense.clean_category("  Food ") == "food"
