import pytest
from conftest import Txn

from app import OrderedMultiSet, consolidate, has_date


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

    def test_it_removes_sliding_window_duplicates_across_three_files(self, make_csv_with_txn):
        coffee = Txn("2024-01-01", "Coffee", 4.50)
        bagel = Txn("2024-01-02", "Bagel", 3.00)
        lunch = Txn("2024-01-03", "Lunch", 12.00)
        tea = Txn("2024-01-04", "Tea", 2.50)
        snack = Txn("2024-01-05", "Snack", 5.00)
        a = make_csv_with_txn("a.csv", [coffee, bagel, lunch])
        b = make_csv_with_txn("b.csv", [bagel, lunch, tea])
        c = make_csv_with_txn("c.csv", [lunch, tea, snack])

        got = consolidate(a, b, c)

        want = "\n".join(
            [
                "date,desc,amount",
                "2024-01-01,Coffee,4.5",
                "2024-01-02,Bagel,3.0",
                "2024-01-03,Lunch,12.0",
                "2024-01-04,Tea,2.5",
                "2024-01-05,Snack,5.0",
            ]
        )
        assert got.strip() == want


class TestHasDate:
    @pytest.mark.parametrize(
        "text, want",
        [
            ("Chase9931_Activity_20260206.CSV", True),
            ("no_date_here.csv", False),
            ("20260101_transactions.csv", True),
            ("file_with_7digits_1234567.csv", False),
        ],
    )
    def test_has_date(self, text: str, want: bool) -> None:
        got = has_date(text)
        assert got == want


class TestOrderedMultiSet:
    def test_extend(self):
        s = OrderedMultiSet()
        s.extend(["a", "b", "b", "c"])
        s.extend(["b", "c", "d"])
        assert s._order == ["a", "b", "b", "c", "d"]
