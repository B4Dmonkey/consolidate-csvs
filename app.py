import csv
from collections.abc import Hashable
from pathlib import Path


class OrderedMultiSet:
    def __init__(self) -> None:
        self._seen: set[Hashable] = set()
        self._order: list[Hashable] = []

    def extend(self, rows: list[Hashable]) -> None:
        for row in rows:
            if row not in self._seen:
                self._order.append(row)
        self._seen.update(rows)


def consolidate(*file_paths: Path) -> str:
    documents = [csv.DictReader(path.open()) for path in file_paths]
    headers = documents[0].fieldnames
    if not headers:
        raise ValueError("CSV file has no headers")
    if not all(doc.fieldnames == headers for doc in documents):
        raise ValueError("Header mismatch across files")

    header_list = list(headers)
    seen = OrderedMultiSet()
    for doc in documents:
        rows = [tuple(row[h] for h in header_list) for row in doc]
        seen.extend(rows)

    lines = [",".join(header_list)]
    for row in seen._order:
        lines.append(",".join(row))  # type: ignore[arg-type]
    return "\n".join(lines) + "\n"
