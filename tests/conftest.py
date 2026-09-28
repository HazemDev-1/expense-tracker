import pytest

from expense_tracker.storage import CsvStorage
from expense_tracker.tracker import ExpenseTracker


@pytest.fixture
def csv_path(tmp_path):
    return tmp_path / "expenses.csv"


@pytest.fixture
def tracker(csv_path):
    return ExpenseTracker(CsvStorage(csv_path))
