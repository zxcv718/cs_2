from __future__ import annotations

import app.infrastructure.constants as c


class Quiz:
    def __init__(
        self,
        question: str,
        choices: list[str],
        answer: int,
        hint: str | None = None,
    ) -> None:
        self.question = self._validate_question(question)
        self.choices = self._validate_choices(choices)
        self.answer = self._validate_answer(answer)
        self.hint = self._validate_hint(hint)

    def is_correct(self, user_answer: int) -> bool:
        return user_answer == self.answer

    def has_hint(self) -> bool:
        return self.hint is not None

    def get_hint_text(self) -> str:
        return self.hint or c.EMPTY_TEXT

    def to_display_data(self) -> dict[str, object]:
        return {
            c.QUIZ_FIELD_QUESTION: self.question,
            c.QUIZ_FIELD_CHOICES: list(self.choices),
            c.QUIZ_FIELD_ANSWER: self.answer,
            c.QUIZ_FIELD_HINT: self.hint,
        }

    def _validate_question(self, question: str) -> str:
        if not isinstance(question, str):
            raise ValueError(c.ERROR_QUESTION_MUST_BE_STRING)
        normalized = question.strip()
        if not normalized:
            raise ValueError(c.ERROR_QUESTION_MUST_NOT_BE_EMPTY)
        return normalized

    def _validate_choices(self, choices: list[str]) -> list[str]:
        if not isinstance(choices, list) or len(choices) != c.CHOICE_COUNT:
            raise ValueError(
                c.ERROR_CHOICES_LENGTH_TEMPLATE.format(choice_count=c.CHOICE_COUNT)
            )

        normalized_choices: list[str] = []
        for choice in choices:
            if not isinstance(choice, str):
                raise ValueError(c.ERROR_CHOICE_MUST_BE_STRING)
            normalized = choice.strip()
            if not normalized:
                raise ValueError(c.ERROR_CHOICE_MUST_NOT_BE_EMPTY)
            normalized_choices.append(normalized)
        return normalized_choices

    def _validate_answer(self, answer: int) -> int:
        if not isinstance(answer, int) or isinstance(answer, bool):
            raise ValueError(c.ERROR_ANSWER_MUST_BE_INTEGER)
        if answer < c.MIN_ANSWER or answer > c.MAX_ANSWER:
            raise ValueError(
                c.ERROR_ANSWER_RANGE_TEMPLATE.format(
                    min_answer=c.MIN_ANSWER,
                    max_answer=c.MAX_ANSWER,
                )
            )
        return answer

    def _validate_hint(self, hint: str | None) -> str | None:
        if hint is None:
            return None
        if not isinstance(hint, str):
            raise ValueError(c.ERROR_HINT_MUST_BE_STRING_OR_NONE)
        normalized = hint.strip()
        if not normalized:
            return None
        return normalized

