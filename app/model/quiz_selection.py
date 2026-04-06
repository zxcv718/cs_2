from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator

from app.model.quiz import Quiz
from app.service.quiz_metrics import QuestionCount


@dataclass(frozen=True)
class QuizSelection:
    items: tuple[Quiz, ...] = field(default_factory=tuple)

    @classmethod
    def from_items(cls, items: list[Quiz]) -> "QuizSelection":
        return cls(tuple(items))

    def __iter__(self) -> Iterator[Quiz]:
        return iter(self.items)

    def total_questions(self) -> QuestionCount:
        return QuestionCount(len(self.items))
