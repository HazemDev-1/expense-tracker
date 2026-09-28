"""The data the app works with."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation


class ValidationError(ValueError):
    """Raised when user input can't become a valid expense."""


@dataclass(frozen=True)
class Expense:
    """One spending record. Frozen, so an expense can't be changed by accident."""

    id: int
    date: date
    amount: Decimal
    category: str
    note: str = ""

    @staticmethod
    def parse_amount(raw: str) -> Decimal:
        """Turn text like '12.50' into Decimal. Money never uses float (0.1 + 0.2 != 0.3)."""
        try:
            value = Decimal(raw.strip())
        except (InvalidOperation, AttributeError):
            raise ValidationError(f"'{raw}' is not a valid amount") from None
        if not value.is_finite() or value <= 0:
            raise ValidationError("Amount must be a positive number")
        return value.quantize(Decimal("0.01"))

    @staticmethod
    def parse_date(raw: str | None) -> date:
        """Accept YYYY-MM-DD, or nothing for today."""
        if not raw:
            return date.today()
        try:
            return date.fromisoformat(raw)
        except ValueError:
            raise ValidationError(f"'{raw}' is not a date (use YYYY-MM-DD)") from None

    @staticmethod
    def clean_category(raw: str) -> str:
        category = raw.strip().lower()
        if not category:
            raise ValidationError("Category is required")
        return category
