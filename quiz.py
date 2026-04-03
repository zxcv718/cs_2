from __future__ import annotations

from constants import CHOICE_COUNT, MAX_ANSWER, MIN_ANSWER


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
        return self.hint or ""

    def to_display_data(self) -> dict[str, object]:
        return {
            "question": self.question,
            "choices": list(self.choices),
            "answer": self.answer,
            "hint": self.hint,
        }

    def _validate_question(self, question: str) -> str:
        if not isinstance(question, str):
            raise ValueError("question must be a string")
        normalized = question.strip()
        if not normalized:
            raise ValueError("question must not be empty")
        return normalized

    def _validate_choices(self, choices: list[str]) -> list[str]:
        if not isinstance(choices, list) or len(choices) != CHOICE_COUNT:
            raise ValueError(f"choices must be a list of {CHOICE_COUNT} items")

        normalized_choices: list[str] = []
        for choice in choices:
            if not isinstance(choice, str):
                raise ValueError("choice must be a string")
            normalized = choice.strip()
            if not normalized:
                raise ValueError("choice must not be empty")
            normalized_choices.append(normalized)
        return normalized_choices

    def _validate_answer(self, answer: int) -> int:
        if not isinstance(answer, int) or isinstance(answer, bool):
            raise ValueError("answer must be an integer")
        if answer < MIN_ANSWER or answer > MAX_ANSWER:
            raise ValueError(f"answer must be between {MIN_ANSWER} and {MAX_ANSWER}")
        return answer

    def _validate_hint(self, hint: str | None) -> str | None:
        if hint is None:
            return None
        if not isinstance(hint, str):
            raise ValueError("hint must be a string or None")
        normalized = hint.strip()
        if not normalized:
            return None
        return normalized

