from decimal import Decimal

import pytest

from expense_tracker.models import ValidationError
from expense_tracker.storage import CsvStorage
from expense_tracker.tracker import ExpenseTracker


def test_add_assigns_increasing_ids(tracker):
    a = tracker.add("10", "food")
    b = tracker.add("5", "transport")
    assert (a.id, b.id) == (1, 2)


def test_data_survives_restart(tracker, csv_path):
    tracker.add("99.99", "Rent", note="September", on="2026-09-01")

    reloaded = ExpenseTracker(CsvStorage(csv_path))

    [e] = reloaded.expenses
    assert e.amount == Decimal("99.99")
    assert e.category == "rent"
    assert e.note == "September"


def test_ids_continue_after_restart_and_delete(tracker, csv_path):
    tracker.add("1", "a")
    tracker.add("2", "b")
    tracker.delete(1)

    reloaded = ExpenseTracker(CsvStorage(csv_path))
    assert reloaded.add("3", "c").id == 3


def test_delete_unknown_id_raises(tracker):
    with pytest.raises(ValidationError):
        tracker.delete(42)


def test_filter_by_month_and_category(tracker):
    tracker.add("10", "food", on="2026-08-31")
    tracker.add("20", "food", on="2026-09-01")
    tracker.add("30", "transport", on="2026-09-15")

    assert [e.amount for e in tracker.filter(month="2026-09")] == [Decimal("20.00"), Decimal("30.00")]
    assert [e.amount for e in tracker.filter(month="2026-09", category="FOOD")] == [Decimal("20.00")]


def test_filter_rejects_bad_month(tracker):
    with pytest.raises(ValidationError):
        tracker.filter(month="2026-13")


def test_summary_totals_and_orders_by_amount(tracker):
    tracker.add("0.10", "coffee", on="2026-09-01")
    tracker.add("0.20", "coffee", on="2026-09-02")
    tracker.add("5", "books", on="2026-09-03")

    s = tracker.summary("2026-09")

    assert s.total == Decimal("5.30")
    assert s.by_category["coffee"] == Decimal("0.30")  # exact, thanks to Decimal
    assert list(s.by_category) == ["books", "coffee"]
    assert s.top_category() == "books"


def test_summary_of_empty_month(tracker):
    s = tracker.summary("2020-01")
    assert s.count == 0 and s.total == 0 and s.top_category() is None


def test_budget_status_over_and_under(tracker):
    tracker.add("80", "food", on="2026-09-10")
    assert tracker.budget_status("100", "2026-09") == (Decimal("80.00"), Decimal("20.00"))
    assert tracker.budget_status("50", "2026-09") == (Decimal("80.00"), Decimal("-30.00"))
