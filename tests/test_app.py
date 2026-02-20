import pytest
from conftest import Txn

from app import consolidate


class TestConsolidate:
    def test_consolidate(self, make_csv_with_txn):
        a = make_csv_with_txn("a.csv", [Txn("2024-01-01", "Coffee", 4.50)])
        got = consolidate(a)
        assert got.strip() == "\n".join(["date,desc,amount", "2024-01-01,Coffee,4.5"])


    def test_consolidate_returns_dupilcates_within_file(self,make_csv_with_txn):
        a = make_csv_with_txn(
            "a.csv",
            [Txn("2024-01-01", "Coffee", 4.50), Txn("2024-01-01", "Coffee", 4.50)],
        )
        got = consolidate(a)
        assert got.strip() == "\n".join(
            ["date,desc,amount", "2024-01-01,Coffee,4.5", "2024-01-01,Coffee,4.5"]
        )


    @pytest.mark.skip(reason="depends on the underlying obeject")
    def test_it_removes_duplicates(self, make_csv_with_txn):
        a = make_csv_with_txn("a.csv", [Txn("2024-01-01", "Coffee", 4.50)])
        b = make_csv_with_txn("b.csv", [Txn("2024-01-01", "Coffee", 4.50)])

        got = consolidate(a, b)

        want = "\n".join(["date,desc,amount", "2024-01-01,Coffee,4.5"])

        assert got.strip() == want
