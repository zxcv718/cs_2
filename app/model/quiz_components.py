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

    def render(self) -> str:
        return self.value


@dataclass(frozen=True)
class QuizPrompt:
    question_text: QuestionText
    choice_set: ChoiceSet

    def render_question_line(self) -> str:
        return self.question_text.value

    def render_choice_lines(self) -> tuple[str, ...]:
        return self.choice_set.values

    def render_choice_line_for(self, answer_number: "AnswerNumber") -> str:
        index = answer_number.value - c.DISPLAY_INDEX_START
        return self.choice_set.values[index]

    def render_listing_lines(self, display_index: int) -> tuple[str, ...]:
        listing_header = c.QUIZ_LIST_ITEM_TEMPLATE.format(
            index=display_index,
            question=self.render_question_line(),
        )
        choice_lines = tuple(
            c.QUIZ_LIST_CHOICE_TEMPLATE.format(
                choice_index=choice_index,
                choice=choice,
            )
            for choice_index, choice in enumerate(
                self.render_choice_lines(),
                start=c.DISPLAY_INDEX_START,
            )
        )
        return (listing_header, *choice_lines)

    def render_question_lines(
        self,
        display_index: int,
        total_questions: int,
    ) -> tuple[str, ...]:
        question_header = c.QUESTION_HEADER_TEMPLATE.format(
            index=display_index,
            total=total_questions,
            question=self.render_question_line(),
        )
        choice_lines = tuple(
            c.QUESTION_CHOICE_TEMPLATE.format(
                choice_index=choice_index,
                choice=choice,
            )
            for choice_index, choice in enumerate(
                self.render_choice_lines(),
                start=c.DISPLAY_INDEX_START,
            )
        )
        return (question_header, *choice_lines)


@dataclass(frozen=True)
class QuizSolution:
    answer_number: AnswerNumber
    hint_text: Optional[HintText] = None

    def matches(self, user_answer: int) -> bool:
        return self.answer_number.value == user_answer

    def can_offer_hint(self) -> bool:
        return self.hint_text is not None

    def render_hint_line(self) -> str:
        if self.hint_text is None:
            return c.EMPTY_TEXT
        return self.hint_text.render()

    def render_wrong_answer_message(self, prompt: QuizPrompt) -> str:
        return c.ERROR_WRONG_ANSWER_TEMPLATE.format(
            answer=self.answer_number.value,
            correct_text=prompt.render_choice_line_for(self.answer_number),
        )
