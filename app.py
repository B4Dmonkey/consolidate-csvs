from collections.abc import Hashable
from pathlib import Path


class OrderedMultiSet:
    def __init__(self) -> None:
        self._seen: set[Hashable] = set()
        self._order: list[Hashable] = []

    def extend(self, rows): ...


def consolidate(*file_paths: Path) -> str:
    headers = [path.open().readline() for path in file_paths]
    if len(set(headers)) > 1:
        raise ValueError("Header mismatch across files")

    return file_paths[0].read_text()
