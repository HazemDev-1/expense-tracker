"""Reading and writing expenses to a CSV file (opens in Excel too)."""

from __future__ import annotations

import csv
import os
from datetime import date
from decimal import Decimal
from pathlib import Path

from .models import Expense

FIELDS = ["id", "date", "amount", "category", "note"]


class CsvStorage:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self) -> list[Expense]:
        if not self.path.exists():
            return []
        with self.path.open(newline="", encoding="utf-8") as f:
            return [
                Expense(
                    id=int(row["id"]),
                    date=date.fromisoformat(row["date"]),
                    amount=Decimal(row["amount"]),
                    category=row["category"],
                    note=row.get("note", ""),
                )
                for row in csv.DictReader(f)
            ]

    def save(self, expenses: list[Expense]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # Write to a temp file, then replace: a crash mid-write never corrupts the real file.
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        with tmp.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            for e in expenses:
                writer.writerow(
                    {"id": e.id, "date": e.date.isoformat(), "amount": str(e.amount),
                     "category": e.category, "note": e.note}
                )
        os.replace(tmp, self.path)
