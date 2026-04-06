from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Iterable, Iterator

from app.model.quiz import Quiz
from app.model.quiz_selection import QuizSelection, QuizSelectionItems
from app.service.quiz_metrics import DisplayIndex, QuestionCount


@dataclass(frozen=True)
class QuizItems:
    values: tuple[Quiz, ...] = field(default_factory=tuple)

    @classmethod
    def from_iterable(cls, quizzes: Iterable[Quiz]) -> "QuizItems":
        return cls(tuple(quizzes))

    def __iter__(self) -> Iterator[Quiz]:
        return iter(self.values)

    def __len__(self) -> int:
        return len(self.values)

    def appended(self, quiz: Quiz) -> "QuizItems":
        return QuizItems(self.values + (quiz,))

    def randomized_selection_items(
        self,
        question_count: QuestionCount,
    ) -> QuizSelectionItems:
        working_items = list(self.values)
        random.shuffle(working_items)
        selected_items = working_items[: int(question_count)]
        return QuizSelectionItems.from_iterable(selected_items)

    def removed_quiz(self, display_index: DisplayIndex) -> Quiz:
        storage_index = display_index.to_storage_index()
        return self.values[storage_index]

    def without(self, display_index: DisplayIndex) -> "QuizItems":
        storage_index = display_index.to_storage_index()
        updated_items = self.values[:storage_index] + self.values[storage_index + 1 :]
        return QuizItems(updated_items)


@dataclass
class QuizCatalog:
    items: QuizItems = field(default_factory=QuizItems)

    def __iter__(self) -> Iterator[Quiz]:
        quiz_items = self.items
        return iter(quiz_items)

    def __len__(self) -> int:
        quiz_items = self.items
        return len(quiz_items)

    def __bool__(self) -> bool:
        quiz_items = self.items
        return bool(len(quiz_items))

    def append(self, quiz: Quiz) -> None:
        quiz_items = self.items
        self.items = quiz_items.appended(quiz)

    def randomized_selection(self, question_count: QuestionCount) -> QuizSelection:
        quiz_items = self.items
        selection_items = quiz_items.randomized_selection_items(question_count)
        return QuizSelection(selection_items)

    def remove_by_display_index(self, display_index: DisplayIndex) -> Quiz:
        quiz_items = self.items
        removed_quiz = quiz_items.removed_quiz(display_index)
        self.items = quiz_items.without(display_index)
        return removed_quiz
