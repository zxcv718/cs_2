from dataclasses import dataclass
from typing import Iterable, Iterator, Optional

import app.config.constants as constants


@dataclass(frozen=True)
class QuestionText:
    value: str

    @classmethod
    def from_raw(cls, question: str) -> "QuestionText":
        if not isinstance(question, str):
            raise ValueError(constants.ERROR_QUESTION_MUST_BE_STRING)
        normalized_question = question.strip()
        if not normalized_question:
            raise ValueError(constants.ERROR_QUESTION_MUST_NOT_BE_EMPTY)
        return cls(normalized_question)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ChoiceDrafts:
    values: tuple[str, ...]

    @classmethod
    def from_iterable(cls, choices: Iterable[str]) -> "ChoiceDrafts":
        choice_values = tuple(cls._choice_texts(choices))
        return cls(choice_values)

    @staticmethod
    def _choice_texts(choices: Iterable[str]) -> Iterator[str]:
        for choice in choices:
            yield ChoiceSet._normalized_choice(choice)

    def __iter__(self) -> Iterator[str]:
        return iter(self.values)


@dataclass(frozen=True)
class ChoiceSet:
    values: tuple[str, ...]

    @classmethod
    def from_drafts(cls, choice_drafts: ChoiceDrafts) -> "ChoiceSet":
        choices = tuple(choice_drafts)
        validated_choices = cls._validated_choices(choices)
        return cls(validated_choices)

    @staticmethod
    def _validated_choices(choices: tuple[str, ...]) -> tuple[str, ...]:
        choice_count = constants.CHOICE_COUNT
        if len(choices) != choice_count:
            error_template = constants.ERROR_CHOICES_LENGTH_TEMPLATE
            raise ValueError(error_template.format(choice_count=choice_count))
        return choices

    @staticmethod
    def _normalized_choice(choice: str) -> str:
        if not isinstance(choice, str):
            raise ValueError(constants.ERROR_CHOICE_MUST_BE_STRING)
        normalized_choice = choice.strip()
        if not normalized_choice:
            raise ValueError(constants.ERROR_CHOICE_MUST_NOT_BE_EMPTY)
        return normalized_choice

    def __iter__(self) -> Iterator[str]:
        return iter(self.values)

    def choice_text(self, answer_number: "AnswerNumber") -> str:
        choice_index = int(answer_number) - constants.DISPLAY_INDEX_START
        return self.values[choice_index]


@dataclass(frozen=True)
class AnswerNumber:
    value: int

    @classmethod
    def from_raw(cls, answer: int) -> "AnswerNumber":
        if cls._is_not_integer(answer):
            raise ValueError(constants.ERROR_ANSWER_MUST_BE_INTEGER)
        if cls._is_out_of_range(answer):
            error_template = constants.ERROR_ANSWER_RANGE_TEMPLATE
            raise ValueError(
                error_template.format(
                    min_answer=constants.MIN_ANSWER,
                    max_answer=constants.MAX_ANSWER,
                )
            )
        return cls(answer)

    @staticmethod
    def _is_not_integer(answer: int) -> bool:
        return not isinstance(answer, int) or isinstance(answer, bool)

    @staticmethod
    def _is_out_of_range(answer: int) -> bool:
        minimum_answer = constants.MIN_ANSWER
        maximum_answer = constants.MAX_ANSWER
        return answer < minimum_answer or answer > maximum_answer

    def __int__(self) -> int:
        return self.value

    def __index__(self) -> int:
        return self.value


@dataclass(frozen=True)
class HintText:
    value: str

    @classmethod
    def from_raw(cls, hint: Optional[str]) -> Optional["HintText"]:
        if hint is None:
            return None
        if not isinstance(hint, str):
            raise ValueError(constants.ERROR_HINT_MUST_BE_STRING_OR_NONE)
        normalized_hint = hint.strip()
        if not normalized_hint:
            return None
        return cls(normalized_hint)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class QuizPrompt:
    question_text: QuestionText
    choice_set: ChoiceSet


@dataclass(frozen=True)
class QuizSolution:
    answer_number: AnswerNumber
    hint_text: Optional[HintText] = None

    def matches(self, user_answer: int) -> bool:
        answer_number = self.answer_number
        return int(answer_number) == user_answer

    def can_offer_hint(self) -> bool:
        return self.hint_text is not None


@dataclass(frozen=True)
class QuizDraftPrompt:
    question_text: QuestionText
    choice_drafts: ChoiceDrafts


@dataclass(frozen=True)
class QuizDraftSolution:
    answer_number: AnswerNumber
    hint_text: Optional[HintText] = None


@dataclass(frozen=True)
class QuizDraft:
    prompt: QuizDraftPrompt
    solution: QuizDraftSolution
