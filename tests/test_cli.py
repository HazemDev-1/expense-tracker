from expense_tracker.cli import main


def run(csv_path, *args):
    return main(["--file", str(csv_path), *args])


def test_add_then_list(csv_path, capsys):
    assert run(csv_path, "add", "12.5", "Food", "--note", "lunch", "--date", "2026-09-20") == 0
    assert run(csv_path, "list") == 0

    out = capsys.readouterr().out
    assert "Added #1: 12.50 on food" in out
    assert "lunch" in out


def test_invalid_amount_returns_error_code(csv_path, capsys):
    assert run(csv_path, "add", "abc", "food") == 1
    assert "not a valid amount" in capsys.readouterr().err


def test_summary_shows_percentages(csv_path, capsys):
    run(csv_path, "add", "75", "rent", "--date", "2026-09-01")
    run(csv_path, "add", "25", "food", "--date", "2026-09-02")
    capsys.readouterr()

    run(csv_path, "summary", "--month", "2026-09")

    out = capsys.readouterr().out
    assert "75.0%" in out and "25.0%" in out
    assert "(2 expenses)" in out


def test_budget_over_limit_exits_with_2(csv_path, capsys):
    run(csv_path, "add", "150", "food", "--date", "2026-09-05")
    assert run(csv_path, "budget", "100", "--month", "2026-09") == 2
    assert "Over budget by 50.00" in capsys.readouterr().out


def test_delete(csv_path, capsys):
    run(csv_path, "add", "5", "misc")
    assert run(csv_path, "delete", "1") == 0
    run(csv_path, "list")
    assert "No expenses found." in capsys.readouterr().out
