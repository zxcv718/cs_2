from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator

from app.application.state.quiz_history_entry import QuizHistoryEntry


@dataclass
class GameHistory:
    entries: list[QuizHistoryEntry] = field(default_factory=list)

    @classmethod
    def from_entries(cls, entries: list[QuizHistoryEntry]) -> "GameHistory":
        return cls(list(entries))

    def __iter__(self) -> Iterator[QuizHistoryEntry]:
        return iter(self.entries)

    def __len__(self) -> int:
        return len(self.entries)

    def append(self, entry: QuizHistoryEntry) -> None:
        entries = self.entries
        entries.append(entry)
