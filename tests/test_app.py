import pytest
from conftest import Txn

from app import OrderedMultiSet, consolidate, has_date


class TestConsolidate:
    def test_consolidate(self, make_csv_with_txn):
        a = make_csv_with_txn("a.csv", [Txn("2024-01-01", "Coffee", 4.50)])
        b = make_csv_with_txn("b.csv", [Txn("2024-01-02", "Bagel", 3.00)])

        got = consolidate(a, b)

        want = "\n".join(["Date,desc,amount", "2024-01-01,Coffee,4.5", "2024-01-02,Bagel,3.0"])
        assert got.strip() == want

    def test_consolidate_returns_dupilcates_within_file(self, make_csv_with_txn):
        a = make_csv_with_txn("a.csv", [Txn("2024-01-01", "Coffee", 4.50), Txn("2024-01-01", "Coffee", 4.50)])
        got = consolidate(a)
        assert got.strip() == "\n".join(["Date,desc,amount", "2024-01-01,Coffee,4.5", "2024-01-01,Coffee,4.5"])

    def test_consolidate_raises_on_mismatched_headers(self, make_csv_with_headers):
        a = make_csv_with_headers("a.csv")
        b = make_csv_with_headers("b.csv", headers=["date", "description", "amount"])

        with pytest.raises(ValueError):
            consolidate(a, b)

    def test_it_removes_duplicates(self, make_csv_with_txn):
        a = make_csv_with_txn("a.csv", [Txn("2024-01-01", "Coffee", 4.50)])
        b = make_csv_with_txn("b.csv", [Txn("2024-01-01", "Coffee", 4.50)])

        got = consolidate(a, b)

        want = "\n".join(["Date,desc,amount", "2024-01-01,Coffee,4.5"])
        assert got.strip() == want

    def test_it_quotes_fields_containing_commas(self, make_csv_with_txn):
        a = make_csv_with_txn("a.csv", [Txn("2024-01-01", "SQ *BED-VYNE BREW, LLC Brooklyn NY", 21.31)])

        got = consolidate(a)

        want = "\n".join(["Date,desc,amount", '2024-01-01,"SQ *BED-VYNE BREW, LLC Brooklyn NY",21.31'])
        assert got.strip() == want

    def test_it_sorts_rows_oldest_first_by_sort_key(self, make_csv_with_txn):
        a = make_csv_with_txn("a.csv", [Txn("2024-01-03", "Lunch", 12.00), Txn("2024-01-01", "Coffee", 4.50)])

        got = consolidate(a, sort_key="date")

        want = "\n".join(["Date,desc,amount", "2024-01-01,Coffee,4.5", "2024-01-03,Lunch,12.0"])
        assert got.strip() == want

    def test_it_excludes_rows_where_required_column_is_empty(self, make_csv_with_headers):
        a = make_csv_with_headers(
            "a.csv",
            headers=["Date", "desc", "amount", "balance"],
            rows=[
                ["2024-01-01", "Coffee", "4.50", "100.00"],
                ["2024-01-02", "Bagel", "3.00", ""],
            ],
        )

        got = consolidate(a, require="balance")

        want = "\n".join(["Date,desc,amount,balance", "2024-01-01,Coffee,4.50,100.00"])
        assert got == want

    def test_require_is_case_insensitive(self, make_csv_with_headers):
        a = make_csv_with_headers(
            "a.csv",
            headers=["Date", "desc", "amount", "Balance"],
            rows=[
                ["2024-01-01", "Coffee", "4.50", "100.00"],
                ["2024-01-02", "Bagel", "3.00", ""],
            ],
        )

        got = consolidate(a, require="balance")

        want = "\n".join(["Date,desc,amount,Balance", "2024-01-01,Coffee,4.50,100.00"])
        assert got == want

    def test_it_sorts_rows_globally_across_files(self, make_csv_with_txn):
        a = make_csv_with_txn("a.csv", [Txn("2024-01-03", "Lunch", 12.00)])
        b = make_csv_with_txn("b.csv", [Txn("2024-01-01", "Coffee", 4.50)])

        got = consolidate(a, b, sort_key="date")

        want = "\n".join(["Date,desc,amount", "2024-01-01,Coffee,4.5", "2024-01-03,Lunch,12.0"])
        assert got == want

    def test_it_preserves_empty_cells_in_output(self, make_csv_with_headers):
        a = make_csv_with_headers(
            "a.csv",
            headers=["Date", "desc", "amount", "balance", "memo"],
            rows=[["2024-01-01", "Coffee", "4.50", " ", ""]],
        )

        got = consolidate(a)

        want = "\n".join(["Date,desc,amount,balance,memo", "2024-01-01,Coffee,4.50, ,"])
        assert got == want

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
                "Date,desc,amount",
                "2024-01-01,Coffee,4.5",
                "2024-01-02,Bagel,3.0",
                "2024-01-03,Lunch,12.0",
                "2024-01-04,Tea,2.5",
                "2024-01-05,Snack,5.0",
            ]
        )
        assert got.strip() == want

    def test_it_sorts_mm_dd_yyyy_dates(self, make_csv_with_headers):
        a = make_csv_with_headers(
            "a.csv",
            headers=["Details", "Posting Date", "Description", "Amount"],
            rows=[
                ["DEBIT", "02/06/2026", "Coffee", "-4.50"],
                ["DEBIT", "01/15/2026", "Bagel", "-3.00"],
                ["DEBIT", "12/31/2025", "Lunch", "-12.00"],
            ],
        )

        got = consolidate(a, sort_key="Posting Date")

        want = "\n".join(
            [
                "Details,Posting Date,Description,Amount",
                "DEBIT,12/31/2025,Lunch,-12.00",
                "DEBIT,01/15/2026,Bagel,-3.00",
                "DEBIT,02/06/2026,Coffee,-4.50",
            ]
        )
        assert got == want

    def test_it_preserves_trailing_empty_columns(self, tmp_path):
        path = tmp_path / "chase.csv"
        path.write_text(
            "Details,Posting Date,Description,Amount,Type,Balance,Check or Slip #\n"
            "DEBIT,10/18/2024,ATM WITHDRAWAL,-100.00,DEBIT_CARD,1954.39,,\n"
        )

        got = consolidate(path, sort_key="Posting Date")

        want = "\n".join(
            [
                "Details,Posting Date,Description,Amount,Type,Balance,Check or Slip #",
                "DEBIT,10/18/2024,ATM WITHDRAWAL,-100.00,DEBIT_CARD,1954.39,,",
            ]
        )
        assert got == want

    def test_it_excludes_rows_where_required_column_is_blank(self, tmp_path):
        path = tmp_path / "chase.csv"
        path.write_text(
            "Details,Posting Date,Description,Amount,Type,Balance,Check or Slip #\n"
            "DEBIT,02/24/2026,POS DEBIT POTBELLY #5280 NEW YORK NY 6649,-14.25,MISC_DEBIT, ,,\n"
            "DEBIT,02/23/2026,ZELLE PAYMENT FROM SMITH,500.00,ACH_CREDIT,2454.39,,\n"
        )

        got = consolidate(path, sort_key="Posting Date", require="Balance")

        want = "\n".join(
            [
                "Details,Posting Date,Description,Amount,Type,Balance,Check or Slip #",
                "DEBIT,02/23/2026,ZELLE PAYMENT FROM SMITH,500.00,ACH_CREDIT,2454.39,,",
            ]
        )
        assert got == want

    def test_it_collapses_whitespace_in_fields(self, make_csv_with_headers):
        a = make_csv_with_headers(
            "a.csv",
            headers=["Date", "desc", "amount"],
            rows=[["2024-01-01", "ORIG CO NAME:VENMO            CO ENTRY DESCR:CASHOUT    SEC:PPD", "4.50"]],
        )

        got = consolidate(a)

        want = "\n".join(["Date,desc,amount", "2024-01-01,ORIG CO NAME:VENMO CO ENTRY DESCR:CASHOUT SEC:PPD,4.50"])
        assert got == want


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

    def test_sort(self):
        s = OrderedMultiSet()
        s.extend(["c", "a", "b"])
        s.sort(lambda x: x)
        assert list(s) == ["a", "b", "c"]
