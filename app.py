from collections.abc import Hashable
from pathlib import Path


class OrderedMultiSet:
    def __init__(self) -> None:
        self._seen: set[Hashable] = set()
        self._order: list[Hashable] = []

    def extend(self, rows): ...


def consolidate(*file_paths: Path) -> str:
    return file_paths[0].read_text()
