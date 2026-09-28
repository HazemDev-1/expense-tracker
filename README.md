# Expense Tracker (Python CLI)

A command-line expense tracker written in **Python** with no third-party runtime dependencies. Expenses are saved to a CSV file you can also open in Excel.

![tests](https://github.com/HazemDev-1/expense-tracker/actions/workflows/tests.yml/badge.svg)

## Features

- Add expenses with amount, category, optional note and date
- List and filter by month and/or category
- Monthly summary: total per category with percentages, sorted by amount
- Budget check: shows what's left, or how much you're over (exit code 2 when over budget)
- Delete by id
- Input validation with clear error messages
- Money uses `Decimal`, so `0.10 + 0.20` is exactly `0.30`
- Safe saves: writes to a temp file then swaps it in, so a crash can't corrupt your data

## Usage

```bash
pip install -e .

expenses add 12.50 food --note "lunch"
expenses add 300 rent --date 2026-09-01
expenses list --month 2026-09
expenses summary --month 2026-09
expenses budget 1000
expenses delete 2
```

Example summary:

```
rent        300.00   96.0%
food         12.50    4.0%
total       312.50  (2 expenses)
```

Use `--file path.csv` (or the `EXPENSES_FILE` environment variable) to choose where data is stored.

## Tests

```bash
pip install -e ".[dev]"
pytest --cov=expense_tracker
```

26 tests, 96% coverage. They run on Python 3.10 and 3.12 in GitHub Actions on every push.

## Structure

| File | Responsibility |
|---|---|
| `models.py` | `Expense` dataclass and input parsing/validation |
| `storage.py` | CSV read/write |
| `tracker.py` | Business logic: add, delete, filter, summary, budget. No printing. |
| `cli.py` | `argparse` commands; the only file that prints |

Keeping logic out of the CLI means every rule is tested directly, and a web or GUI front end could reuse `tracker.py` as is.
