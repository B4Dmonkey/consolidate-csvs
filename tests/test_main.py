import subprocess
from pathlib import Path

import pytest
from conftest import Txn


@pytest.fixture
def run():
    CMD = "consolidate-csvs"
    return lambda *args: subprocess.run([CMD, *map(str, args)], capture_output=True, text=True)


def test_main(run, make_csv_file):
    test_file: Path = make_csv_file()
    got = run(test_file)
    assert got.returncode == 0
    assert got.stdout.strip() == test_file.read_text().strip()


def test_it_does_not_remove_dupes_within_same_csv(run, make_csv_with_txn):
    txns = [Txn("2024-01-01", "Coffee", 4.50), Txn("2024-01-01", "Coffee", 4.50)]
    test_file: Path = make_csv_with_txn("a.csv", txns)
    got = run(test_file)
    assert got.returncode == 0

    want = "\n".join(
        [
            "Date,desc,amount",
            "2024-01-01,Coffee,4.5",
            "2024-01-01,Coffee,4.5",
        ]
    )

    assert got.stdout.strip() == want


def test_it_removes_dupes_across_files(run, make_csv_with_txn):
    a = make_csv_with_txn("a.csv", [Txn("2024-01-01", "Coffee", 4.50)])
    b = make_csv_with_txn("b.csv", [Txn("2024-01-01", "Coffee", 4.50)])

    got = run(a, b)

    assert got.returncode == 0
    assert got.stdout.strip() == "\n".join(["Date,desc,amount", "2024-01-01,Coffee,4.5"])


def test_it_combines_multiple_csv_inputs(run, make_csv_with_txn):
    a = make_csv_with_txn("a.csv", [Txn("2024-01-01", "Coffee", 4.50)])
    b = make_csv_with_txn("b.csv", [Txn("2024-01-02", "Bagel", 3.00)])

    got = run(a, b)

    assert got.returncode == 0

    want = "\n".join(
        [
            "Date,desc,amount",
            "2024-01-01,Coffee,4.5",
            "2024-01-02,Bagel,3.0",
        ]
    )

    assert got.stdout.strip() == want


def test_it_sorts_inputs_by_date_in_filename(run, make_csv_with_txn):
    coffee = Txn("2024-01-01", "Coffee", 4.50)
    bagel = Txn("2024-01-02", "Bagel", 3.00)
    lunch = Txn("2024-01-03", "Lunch", 12.00)
    tea = Txn("2024-01-04", "Tea", 2.50)
    snack = Txn("2024-01-05", "Snack", 5.00)

    a = make_csv_with_txn("Chase9931_Activity_20240103.CSV", [lunch, tea, snack])
    b = make_csv_with_txn("Chase9931_Activity_20240101.CSV", [coffee, bagel, lunch])
    c = make_csv_with_txn("Chase9931_Activity_20240102.CSV", [bagel, lunch, tea])

    got = run(a, b, c)

    assert got.returncode == 0

    want = "\n".join(
        [
            "Date,desc,amount",
            "2024-01-01,Coffee,4.5",
            "2024-01-02,Bagel,3.0",
            "2024-01-03,Lunch,12.0",
            "2024-01-04,Tea,2.5",
            "2024-01-05,Snack,5.0",
        ]
    )

    assert got.stdout.strip() == want


def test_out_option_writes_to_file(run, make_csv_with_txn, tmp_path):
    a = make_csv_with_txn("a.csv", [Txn("2024-01-01", "Coffee", 4.50)])
    out_file = tmp_path / "out.csv"

    got = run(a, "--out", out_file)

    assert got.returncode == 0
    assert out_file.read_text().strip() == "Date,desc,amount\n2024-01-01,Coffee,4.5"


def test_sort_key_option(run, make_csv_with_txn):
    a = make_csv_with_txn("a.csv", [Txn("2024-01-03", "Lunch", 12.00), Txn("2024-01-01", "Coffee", 4.50)])

    got = run(a, "--sort-key", "date")

    assert got.returncode == 0

    want = "\n".join(
        [
            "Date,desc,amount",
            "2024-01-01,Coffee,4.5",
            "2024-01-03,Lunch,12.0",
        ]
    )

    assert got.stdout.strip() == want


def test_require_option_excludes_rows_with_empty_column(run, make_csv_with_headers):
    a = make_csv_with_headers(
        "a.csv",
        headers=["Date", "desc", "amount", "balance"],
        rows=[
            ["2024-01-01", "Coffee", "4.50", "100.00"],
            ["2024-01-02", "Bagel", "3.00", ""],
        ],
    )

    got = run(a, "--require", "balance")

    assert got.returncode == 0
    assert got.stdout.strip() == "Date,desc,amount,balance\n2024-01-01,Coffee,4.50,100.00"
