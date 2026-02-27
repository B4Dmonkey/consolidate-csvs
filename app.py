import csv
import io
import re
from collections.abc import Callable, Hashable
from datetime import datetime
from pathlib import Path
from typing import Any


class OrderedMultiSet:
    def __init__(self) -> None:
        self._seen: set[Hashable] = set()
        self._order: list[Hashable] = []

    def __iter__(self):
        return iter(self._order)

    def sort(self, key: Callable[[Hashable], Any]) -> None:
        self._order.sort(key=key)

    def extend(self, rows: list[Hashable]) -> None:
        for row in rows:
            if row not in self._seen:
                self._order.append(row)
        self._seen.update(rows)


DATE_FORMATS = ["%m/%d/%Y", "%Y-%m-%d"]


def parse_date(text: str) -> str:
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return text


def has_date(text: str) -> bool:
    return bool(re.search(r"\d{8}", text))


def consolidate(*file_paths: Path, sort_key: str = "date", require: str | None = None) -> str:
    documents = [csv.DictReader(path.open()) for path in file_paths]
    headers = documents[0].fieldnames
    if not headers:
        raise ValueError("CSV file has no headers")
    if not all(doc.fieldnames == headers for doc in documents):
        raise ValueError("Header mismatch across files")

    headers_lower = [h.lower() for h in headers]
    if require and require.lower() in headers_lower:
        require = headers[headers_lower.index(require.lower())]

    seen = OrderedMultiSet()
    extra_columns = 0
    for doc in documents:
        rows = []
        for row in doc:
            if require and not row.get(require, "").strip():
                continue
            values = tuple(re.sub(r" {2,}", " ", row[h]) for h in headers)
            extra = row.get(None, [])
            if extra:
                values = values + tuple(extra)
                extra_columns = max(extra_columns, len(extra))
            rows.append(values)
        seen.extend(rows)
    if sort_key.lower() in headers_lower:
        key_index = headers_lower.index(sort_key.lower())
        seen.sort(key=lambda r: parse_date(r[key_index]))

    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(headers)
    writer.writerows(seen)
    return output.getvalue().strip()
