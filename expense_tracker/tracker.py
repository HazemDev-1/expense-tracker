"""All the business logic. No printing, no input(): the CLI handles that."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from .models import Expense, ValidationError
from .storage import CsvStorage


@dataclass(frozen=True)
class Summary:
    total: Decimal
    by_category: dict[str, Decimal]
    count: int

    def top_category(self) -> str | None:
        if not self.by_category:
            return None
        return max(self.by_category, key=self.by_category.__getitem__)


class ExpenseTracker:
    def __init__(self, storage: CsvStorage) -> None:
        self._storage = storage
        self._expenses = storage.load()

    @property
    def expenses(self) -> list[Expense]:
        return list(self._expenses)

    def add(self, amount: str, category: str, note: str = "", on: str | None = None) -> Expense:
        expense = Expense(
            id=self._next_id(),
            date=Expense.parse_date(on),
            amount=Expense.parse_amount(amount),
            category=Expense.clean_category(category),
            note=note.strip(),
        )
        self._expenses.append(expense)
        self._storage.save(self._expenses)
        return expense

    def delete(self, expense_id: int) -> Expense:
        for i, e in enumerate(self._expenses):
            if e.id == expense_id:
                removed = self._expenses.pop(i)
                self._storage.save(self._expenses)
                return removed
        raise ValidationError(f"No expense with id {expense_id}")

    def filter(self, month: str | None = None, category: str | None = None) -> list[Expense]:
        """month is 'YYYY-MM'. Results are sorted oldest first."""
        year_month = _parse_month(month) if month else None
        cat = category.strip().lower() if category else None
        result = [
            e for e in self._expenses
            if (year_month is None or (e.date.year, e.date.month) == year_month)
            and (cat is None or e.category == cat)
        ]
        return sorted(result, key=lambda e: (e.date, e.id))

    def summary(self, month: str | None = None) -> Summary:
        items = self.filter(month=month)
        totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
        for e in items:
            totals[e.category] += e.amount
        ordered = dict(sorted(totals.items(), key=lambda kv: kv[1], reverse=True))
        return Summary(total=sum(ordered.values(), Decimal("0")), by_category=ordered, count=len(items))

    def budget_status(self, limit: str, month: str | None = None) -> tuple[Decimal, Decimal]:
        """Returns (spent, remaining). Remaining is negative when over budget."""
        budget = Expense.parse_amount(limit)
        spent = self.summary(month or date.today().strftime("%Y-%m")).total
        return spent, budget - spent

    def _next_id(self) -> int:
        return max((e.id for e in self._expenses), default=0) + 1


def _parse_month(raw: str) -> tuple[int, int]:
    try:
        year, month = (int(p) for p in raw.split("-"))
        if not 1 <= month <= 12:
            raise ValueError
        return year, month
    except ValueError:
        raise ValidationError(f"'{raw}' is not a month (use YYYY-MM)") from None
