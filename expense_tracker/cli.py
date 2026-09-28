"""Command-line interface: parses arguments, calls the tracker, prints results."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Sequence

from .models import ValidationError
from .storage import CsvStorage
from .tracker import ExpenseTracker

DEFAULT_FILE = os.environ.get("EXPENSES_FILE", "expenses.csv")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="expenses", description="Track your spending from the terminal.")
    parser.add_argument("--file", default=DEFAULT_FILE, help="CSV file to use (default: %(default)s)")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="record an expense")
    add.add_argument("amount")
    add.add_argument("category")
    add.add_argument("--note", default="")
    add.add_argument("--date", help="YYYY-MM-DD (default: today)")

    ls = sub.add_parser("list", help="show expenses")
    ls.add_argument("--month", help="YYYY-MM")
    ls.add_argument("--category")

    summary = sub.add_parser("summary", help="totals per category")
    summary.add_argument("--month", help="YYYY-MM")

    budget = sub.add_parser("budget", help="compare this month's spending to a limit")
    budget.add_argument("limit")
    budget.add_argument("--month", help="YYYY-MM (default: this month)")

    delete = sub.add_parser("delete", help="remove an expense by id")
    delete.add_argument("id", type=int)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    tracker = ExpenseTracker(CsvStorage(args.file))

    try:
        if args.command == "add":
            e = tracker.add(args.amount, args.category, args.note, args.date)
            print(f"Added #{e.id}: {e.amount} on {e.category} ({e.date})")

        elif args.command == "list":
            items = tracker.filter(args.month, args.category)
            if not items:
                print("No expenses found.")
            for e in items:
                note = f"  {e.note}" if e.note else ""
                print(f"#{e.id:<4} {e.date}  {e.amount:>10}  {e.category:<12}{note}")

        elif args.command == "summary":
            s = tracker.summary(args.month)
            if s.count == 0:
                print("No expenses found.")
                return 0
            width = max(len(c) for c in s.by_category)
            for category, amount in s.by_category.items():
                share = amount / s.total * 100
                print(f"{category:<{width}}  {amount:>10}  {share:5.1f}%")
            print(f"{'total':<{width}}  {s.total:>10}  ({s.count} expenses)")

        elif args.command == "budget":
            spent, remaining = tracker.budget_status(args.limit, args.month)
            if remaining >= 0:
                print(f"Spent {spent}. {remaining} left in your budget.")
            else:
                print(f"Spent {spent}. Over budget by {-remaining}!")
                return 2

        elif args.command == "delete":
            e = tracker.delete(args.id)
            print(f"Deleted #{e.id} ({e.amount} on {e.category})")

    except ValidationError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
