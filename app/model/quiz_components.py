from dataclasses import dataclass
from typing import Optional

import app.config.constants as c


@dataclass(frozen=True)
class QuestionText:
    value: str

    @classmethod
    def from_raw(cls, question: str) -> "QuestionText":
        if not isinstance(question, str):
            raise ValueError(c.ERROR_QUESTION_MUST_BE_STRING)

        normalized = question.strip()
        if not normalized:
            raise ValueError(c.ERROR_QUESTION_MUST_NOT_BE_EMPTY)
        return cls(normalized)


@dataclass(frozen=True)
class ChoiceSet:
    values: tuple[str, ...]

    @classmethod
    def from_raw(cls, choices: list[str]) -> "ChoiceSet":
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
        return cls(tuple(normalized_choices))


@dataclass(frozen=True)
class AnswerNumber:
    value: int

    @classmethod
    def from_raw(cls, answer: int) -> "AnswerNumber":
        if not isinstance(answer, int) or isinstance(answer, bool):
            raise ValueError(c.ERROR_ANSWER_MUST_BE_INTEGER)
        if answer < c.MIN_ANSWER or answer > c.MAX_ANSWER:
            raise ValueError(
                c.ERROR_ANSWER_RANGE_TEMPLATE.format(
                    min_answer=c.MIN_ANSWER,
                    max_answer=c.MAX_ANSWER,
                )
            )
        return cls(answer)


@dataclass(frozen=True)
class HintText:
    value: str

    @classmethod
    def from_raw(cls, hint: Optional[str]) -> Optional["HintText"]:
        if hint is None:
            return None
        if not isinstance(hint, str):
            raise ValueError(c.ERROR_HINT_MUST_BE_STRING_OR_NONE)

        normalized = hint.strip()
        if not normalized:
            return None
        return cls(normalized)
