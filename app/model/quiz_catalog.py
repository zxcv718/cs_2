from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Iterator

import app.config.constants as c
from app.model.quiz import Quiz


@dataclass
class QuizCatalog:
    items: list[Quiz] = field(default_factory=list)

    @classmethod
    def from_items(cls, items: list[Quiz]) -> "QuizCatalog":
        return cls(list(items))

    def __iter__(self) -> Iterator[Quiz]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def append(self, quiz: Quiz) -> None:
        self.items.append(quiz)

    def has_items(self) -> bool:
        return bool(self.items)

    def display_count(self) -> int:
        return len(self.items)

    def randomized_selection(self, question_count: int) -> list[Quiz]:
        working_items = list(self.items)
        random.shuffle(working_items)
        return working_items[:question_count]

    def remove_by_display_index(self, display_index: int) -> Quiz:
        storage_index = display_index - c.DISPLAY_INDEX_START
        return self.items.pop(storage_index)

    def persistable_items(self) -> list[Quiz]:
        return list(self.items)
