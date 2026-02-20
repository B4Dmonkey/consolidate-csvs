from conftest import Txn

from app import consolidate


def test_consolidate(make_csv_with_txn):
    a = make_csv_with_txn("a.csv", [Txn("2024-01-01", "Coffee", 4.50)])
    got= consolidate([a])
    assert got.strip() == "\n".join(
        ["date,desc,amount", "2024-01-01,Coffee,4.5"]
    )
