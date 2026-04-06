from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterator


@dataclass
class GameHistory:
    entries: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_entries(cls, entries: list[dict[str, Any]]) -> "GameHistory":
        return cls(list(entries))

    def __iter__(self) -> Iterator[dict[str, Any]]:
        return iter(self.entries)

    def __len__(self) -> int:
        return len(self.entries)

    def append(self, entry: dict[str, Any]) -> None:
        self.entries.append(entry)
