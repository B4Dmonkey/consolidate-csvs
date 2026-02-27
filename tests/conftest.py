import builtins
import csv
import subprocess
from collections.abc import Callable
from pathlib import Path
from pprint import pprint
from typing import NamedTuple

import pytest

# include pprint as a builtin
builtins.pprint = pprint  # ty:ignore[unresolved-attribute]


type csv_factory = Callable[..., Path]


@pytest.fixture
def run():
    CMD = "consolidate-csvs"
    return lambda *args: subprocess.run([CMD, *map(str, args)], capture_output=True, text=True)


class Txn(NamedTuple):
    date: str
    desc: str
    amount: float


@pytest.fixture
def make_csv_with_headers(tmp_path: Path):
    def factory(
        filename: str = "example.csv", headers: list[str] | None = None, rows: list[list] | None = None
    ) -> Path:
        if headers is None:
            headers = ["Date", "desc", "amount"]
        path = tmp_path / filename
        with path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            if rows:
                writer.writerows(rows)
        return path

    return factory


@pytest.fixture
def make_csv_with_txn(make_csv_with_headers):
    def factory(filename: str, txns: list[Txn]) -> Path:
        return make_csv_with_headers(filename, rows=[(t.date, t.desc, t.amount) for t in txns])

    return factory
