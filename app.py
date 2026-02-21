import csv
import io
import re
from collections.abc import Hashable
from pathlib import Path


class OrderedMultiSet:
    def __init__(self) -> None:
        self._seen: set[Hashable] = set()
        self._order: list[Hashable] = []

    def __iter__(self):
        return iter(self._order)

    def extend(self, rows: list[Hashable]) -> None:
        for row in rows:
            if row not in self._seen:
                self._order.append(row)
        self._seen.update(rows)


def has_date(text: str) -> bool:
    return bool(re.search(r"\d{8}", text))


def consolidate(*file_paths: Path, sort_key: str = "date") -> str:
    documents = [csv.DictReader(path.open()) for path in file_paths]
    headers = documents[0].fieldnames
    if not headers:
        raise ValueError("CSV file has no headers")
    if not all(doc.fieldnames == headers for doc in documents):
        raise ValueError("Header mismatch across files")

    seen = OrderedMultiSet()
    for doc in documents:
        rows = [tuple(row[h] for h in headers) for row in doc]
        headers_lower = [h.lower() for h in headers]
        if sort_key.lower() in headers_lower:
            key_index = headers_lower.index(sort_key.lower())
            rows.sort(key=lambda r: r[key_index])
        seen.extend(rows)

    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(headers)
    writer.writerows(seen)
    return output.getvalue().strip()
