import csv
import subprocess
from pathlib import Path
from typing import NamedTuple

import pytest


class Txn(NamedTuple):
    date: str
    desc: str
    amount: float


@pytest.fixture
def make_csv_file(tmp_path: Path):
    def factory(filename: str = "example.csv") -> Path:
        path = tmp_path / filename
        with path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "desc", "amount"])
        return path

    return factory


@pytest.fixture
def make_csv_with_txn(make_csv_file):
    def factory(filename: str, txns: list[Txn]) -> Path:
        path = make_csv_file(filename)
        with path.open("a", newline="") as f:
            writer = csv.writer(f)
            writer.writerows((t.date, t.desc, t.amount) for t in txns)
        return path

    return factory


@pytest.fixture
def run():
    CMD = "consolidate-csvs"
    return lambda *args: subprocess.run(
        [CMD, *map(str, args)], capture_output=True, text=True
    )


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
            "date,desc,amount",
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
    assert got.stdout.strip() == "\n".join(
        ["date,desc,amount", "2024-01-01,Coffee,4.5"]
    )


def test_it_combines_multiple_csv_inputs(run, make_csv_with_txn):
    a = make_csv_with_txn("a.csv", [Txn("2024-01-01", "Coffee", 4.50)])
    b = make_csv_with_txn("b.csv", [Txn("2024-01-02", "Bagel", 3.00)])

    got = run(a, b)

    assert got.returncode == 0

    want = "\n".join(
        [
            "date,desc,amount",
            "2024-01-01,Coffee,4.5",
            "2024-01-02,Bagel,3.0",
        ]
    )

    assert got.stdout.strip() == want
