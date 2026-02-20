import pytest
from conftest import Txn

from app import OrderedMultiSet, consolidate


class TestConsolidate:
    def test_consolidate(self, make_csv_with_txn):
        a = make_csv_with_txn("a.csv", [Txn("2024-01-01", "Coffee", 4.50)])
        b = make_csv_with_txn("b.csv", [Txn("2024-01-02", "Bagel", 3.00)])

        got = consolidate(a, b)

        want = "\n".join(["date,desc,amount", "2024-01-01,Coffee,4.5", "2024-01-02,Bagel,3.0"])
        assert got.strip() == want

    def test_consolidate_returns_dupilcates_within_file(self, make_csv_with_txn):
        a = make_csv_with_txn("a.csv", [Txn("2024-01-01", "Coffee", 4.50), Txn("2024-01-01", "Coffee", 4.50)])
        got = consolidate(a)
        assert got.strip() == "\n".join(["date,desc,amount", "2024-01-01,Coffee,4.5", "2024-01-01,Coffee,4.5"])

    def test_consolidate_raises_on_mismatched_headers(self, make_csv_with_headers):
        a = make_csv_with_headers("a.csv")
        b = make_csv_with_headers("b.csv", headers=["date", "description", "amount"])

        with pytest.raises(ValueError):
            consolidate(a, b)

    def test_it_removes_duplicates(self, make_csv_with_txn):
        a = make_csv_with_txn("a.csv", [Txn("2024-01-01", "Coffee", 4.50)])
        b = make_csv_with_txn("b.csv", [Txn("2024-01-01", "Coffee", 4.50)])

        got = consolidate(a, b)

        want = "\n".join(["date,desc,amount", "2024-01-01,Coffee,4.5"])
        assert got.strip() == want


class TestOrderedMultiSet:
    def test_extend(self):
        s = OrderedMultiSet()
        s.extend(["a", "b", "b", "c"])
        s.extend(["b", "c", "d"])
        assert s._order == ["a", "b", "b", "c", "d"]
