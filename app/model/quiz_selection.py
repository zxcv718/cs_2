from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Iterator

from app.model.quiz import Quiz
from app.service.quiz_metrics import QuestionCount


@dataclass(frozen=True)
class QuizSelectionItems:
    values: tuple[Quiz, ...] = field(default_factory=tuple)

    @classmethod
    def from_iterable(cls, quizzes: Iterable[Quiz]) -> "QuizSelectionItems":
        return cls(tuple(quizzes))

    def __iter__(self) -> Iterator[Quiz]:
        return iter(self.values)

    def __len__(self) -> int:
        return len(self.values)


@dataclass(frozen=True)
class QuizSelection:
    items: QuizSelectionItems

    def __iter__(self) -> Iterator[Quiz]:
        selection_items = self.items
        return iter(selection_items)

    def total_questions(self) -> QuestionCount:
        selection_items = self.items
        return QuestionCount(len(selection_items))
