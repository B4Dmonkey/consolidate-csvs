import csv
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
