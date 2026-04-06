from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Iterator

import app.config.constants as constants
from app.model.quiz import Quiz
from app.model.quiz_selection import QuizSelection
from app.service.quiz_metrics import DisplayIndex, QuestionCount


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

    def __bool__(self) -> bool:
        return bool(self.items)

    def append(self, quiz: Quiz) -> None:
        items = self.items
        items.append(quiz)

    def randomized_selection(self, question_count: QuestionCount) -> QuizSelection:
        working_items = list(self.items)
        random.shuffle(working_items)
        return QuizSelection.from_items(working_items[: int(question_count)])

    def remove_by_display_index(self, display_index: DisplayIndex) -> Quiz:
        items = self.items
        storage_index = display_index.to_storage_index()
        return items.pop(storage_index)
