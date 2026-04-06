from dataclasses import dataclass
from typing import Optional

import app.config.constants as constants
from app.service.quiz_metrics import DisplayIndex, QuestionCount


@dataclass(frozen=True)
class QuestionText:
    value: str

    @classmethod
    def from_raw(cls, question: str) -> "QuestionText":
        if not isinstance(question, str):
            raise ValueError(constants.ERROR_QUESTION_MUST_BE_STRING)

        normalized = question.strip()
        if not normalized:
            raise ValueError(constants.ERROR_QUESTION_MUST_NOT_BE_EMPTY)
        return cls(normalized)


@dataclass(frozen=True)
class ChoiceSet:
    values: tuple[str, ...]

    @classmethod
    def from_raw(cls, choices: list[str]) -> "ChoiceSet":
        validated_choices = cls._validated_choices(choices)
        normalized_choices = tuple(
            cls._normalized_choice(choice) for choice in validated_choices
        )
        return cls(normalized_choices)

    @staticmethod
    def _validated_choices(choices: list[str]) -> list[str]:
        choice_count = constants.CHOICE_COUNT
        if isinstance(choices, list) and len(choices) == choice_count:
            return choices
        error_template = constants.ERROR_CHOICES_LENGTH_TEMPLATE
        raise ValueError(error_template.format(choice_count=choice_count))

    @staticmethod
    def _normalized_choice(choice: str) -> str:
        if not isinstance(choice, str):
            raise ValueError(constants.ERROR_CHOICE_MUST_BE_STRING)
        normalized = choice.strip()
        if not normalized:
            raise ValueError(constants.ERROR_CHOICE_MUST_NOT_BE_EMPTY)
        return normalized


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

        normalized = hint.strip()
        if not normalized:
            return None
        return cls(normalized)

    def render(self) -> str:
        return self.value


@dataclass(frozen=True)
class QuizPrompt:
    question_text: QuestionText
    choice_set: ChoiceSet

    def render_question_line(self) -> str:
        question_text = self.question_text
        return question_text.value

    def render_choice_lines(self) -> tuple[str, ...]:
        choice_set = self.choice_set
        return choice_set.values

    def render_choice_line_for(self, answer_number: "AnswerNumber") -> str:
        answer = int(answer_number)
        index = answer - constants.DISPLAY_INDEX_START
        choice_lines = self.render_choice_lines()
        return choice_lines[index]

    def render_listing_lines(self, display_index: DisplayIndex) -> tuple[str, ...]:
        listing_template = constants.QUIZ_LIST_ITEM_TEMPLATE
        question_line = self.render_question_line()
        listing_header = listing_template.format(
            index=int(display_index),
            question=question_line,
        )
        choice_lines = self._listing_choice_lines()
        return (listing_header, *choice_lines)

    def render_question_lines(
        self,
        display_index: DisplayIndex,
        total_questions: QuestionCount,
    ) -> tuple[str, ...]:
        header_template = constants.QUESTION_HEADER_TEMPLATE
        question_line = self.render_question_line()
        question_header = header_template.format(
            index=int(display_index),
            total=int(total_questions),
            question=question_line,
        )
        choice_lines = self._question_choice_lines()
        return (question_header, *choice_lines)

    def _listing_choice_lines(self) -> tuple[str, ...]:
        choice_template = constants.QUIZ_LIST_CHOICE_TEMPLATE
        return self._choice_lines(choice_template)

    def _question_choice_lines(self) -> tuple[str, ...]:
        choice_template = constants.QUESTION_CHOICE_TEMPLATE
        return self._choice_lines(choice_template)

    def _choice_lines(self, choice_template: str) -> tuple[str, ...]:
        choice_lines = self.render_choice_lines()
        start = constants.DISPLAY_INDEX_START
        return tuple(
            choice_template.format(
                choice_index=choice_index,
                choice=choice,
            )
            for choice_index, choice in enumerate(choice_lines, start=start)
        )


@dataclass(frozen=True)
class QuizSolution:
    answer_number: AnswerNumber
    hint_text: Optional[HintText] = None

    def matches(self, user_answer: int) -> bool:
        answer_number = self.answer_number
        return int(answer_number) == user_answer

    def can_offer_hint(self) -> bool:
        return self.hint_text is not None

    def render_hint_line(self) -> str:
        if self.hint_text is None:
            return constants.EMPTY_TEXT
        hint_text = self.hint_text
        return hint_text.render()

    def render_wrong_answer_message(self, prompt: QuizPrompt) -> str:
        answer_number = self.answer_number
        correct_choice_line = prompt.render_choice_line_for(answer_number)
        error_template = constants.ERROR_WRONG_ANSWER_TEMPLATE
        return error_template.format(
            answer=int(answer_number),
            correct_text=correct_choice_line,
        )
