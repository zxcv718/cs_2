from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Iterator

from app.application.state.quiz_history_entry import QuizHistoryEntry


@dataclass(frozen=True)
class HistoryEntries:
    values: tuple[QuizHistoryEntry, ...] = field(default_factory=tuple)

    @classmethod
    def from_iterable(cls, entries: Iterable[QuizHistoryEntry]) -> "HistoryEntries":
        return cls(tuple(entries))

    def __iter__(self) -> Iterator[QuizHistoryEntry]:
        return iter(self.values)

    def __len__(self) -> int:
        return len(self.values)

    def appended(self, entry: QuizHistoryEntry) -> "HistoryEntries":
        return HistoryEntries(self.values + (entry,))


@dataclass
class GameHistory:
    entries: HistoryEntries = field(default_factory=HistoryEntries)

    def __iter__(self) -> Iterator[QuizHistoryEntry]:
        history_entries = self.entries
        return iter(history_entries)

    def __len__(self) -> int:
        history_entries = self.entries
        return len(history_entries)

    def append(self, entry: QuizHistoryEntry) -> None:
        history_entries = self.entries
        self.entries = history_entries.appended(entry)
