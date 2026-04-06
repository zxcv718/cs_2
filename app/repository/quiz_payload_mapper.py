from dataclasses import dataclass
from typing import Optional, cast

import app.config.constants as constants
from app.model.quiz import Quiz
from app.model.quiz_components import (
    AnswerNumber,
    ChoiceDrafts,
    HintText,
    QuestionText,
    QuizDraft,
    QuizDraftPrompt,
    QuizDraftSolution,
)
from app.model.quiz_factory import QuizFactory


@dataclass(frozen=True)
class QuizPayloadPrompt:
    question_text: QuestionText
    choice_drafts: ChoiceDrafts


@dataclass(frozen=True)
class QuizPayloadSolution:
    answer_number: AnswerNumber
    hint_text: HintText | None = None


@dataclass(frozen=True)
class QuizPayloadItem:
    prompt: QuizPayloadPrompt
    solution: QuizPayloadSolution


class QuizPayloadMapper:
    def __init__(self, quiz_factory: Optional[QuizFactory] = None) -> None:
        self.quiz_factory = quiz_factory or QuizFactory()

    def to_payload_item(self, quiz: Quiz) -> QuizPayloadItem:
        if not isinstance(quiz, Quiz):
            raise ValueError(constants.ERROR_QUIZ_MUST_BE_INSTANCE)
        prompt = quiz.prompt
        solution = quiz.solution
        choice_set = prompt.choice_set
        choice_values = tuple(choice_set)
        return QuizPayloadItem(
            prompt=QuizPayloadPrompt(
                prompt.question_text,
                ChoiceDrafts(choice_values),
            ),
            solution=QuizPayloadSolution(
                solution.answer_number,
                solution.hint_text,
            ),
        )

    def from_payload_item(self, payload_item: QuizPayloadItem) -> Quiz:
        quiz_factory = self.quiz_factory
        prompt = payload_item.prompt
        solution = payload_item.solution
        quiz_draft = QuizDraft(
            prompt=QuizDraftPrompt(
                prompt.question_text,
                prompt.choice_drafts,
            ),
            solution=QuizDraftSolution(
                solution.answer_number,
                solution.hint_text,
            ),
        )
        return quiz_factory.create(quiz_draft)

    def _payload_item(self, payload_source: object) -> QuizPayloadItem:
        return QuizPayloadItem(
            prompt=QuizPayloadPrompt(
                self._question_text(payload_source),
                self._choice_drafts(payload_source),
            ),
            solution=QuizPayloadSolution(
                self._answer_number(payload_source),
                self._hint_text(payload_source),
            ),
        )

    def _payload_dictionary(self, payload_item: QuizPayloadItem) -> object:
        prompt = payload_item.prompt
        solution = payload_item.solution
        choice_drafts = prompt.choice_drafts
        choice_values = choice_drafts.values
        payload_dictionary: dict[str, object] = {
            constants.QUIZ_FIELD_QUESTION: str(prompt.question_text),
            constants.QUIZ_FIELD_CHOICES: list(choice_values),
            constants.QUIZ_FIELD_ANSWER: int(solution.answer_number),
        }
        hint_text = solution.hint_text
        if hint_text is None:
            return payload_dictionary
        payload_dictionary[constants.QUIZ_FIELD_HINT] = str(hint_text)
        return payload_dictionary

    def _dictionary(self, payload_source: object) -> object:
        if isinstance(payload_source, dict):
            return cast(dict[str, object], payload_source)
        raise ValueError(constants.ERROR_QUIZ_ITEM_MUST_BE_DICTIONARY)

    def _question_text(self, payload_source: object) -> QuestionText:
        payload_dictionary = cast(dict[str, object], self._dictionary(payload_source))
        question_key = constants.QUIZ_FIELD_QUESTION
        question = payload_dictionary.get(question_key)
        if not isinstance(question, str) or not question.strip():
            raise ValueError(constants.ERROR_QUESTION_MUST_BE_NON_EMPTY_STRING)
        return QuestionText.from_raw(question)

    def _choice_drafts(self, payload_source: object) -> ChoiceDrafts:
        payload_dictionary = cast(dict[str, object], self._dictionary(payload_source))
        choices_key = constants.QUIZ_FIELD_CHOICES
        choice_values_from_payload = payload_dictionary.get(choices_key)
        if not isinstance(choice_values_from_payload, list) or len(choice_values_from_payload) != constants.CHOICE_COUNT:
            error_template = constants.ERROR_CHOICES_LENGTH_TEMPLATE
            raise ValueError(error_template.format(choice_count=constants.CHOICE_COUNT))
        return ChoiceDrafts.from_iterable(choice_values_from_payload)

    def _answer_number(self, payload_source: object) -> AnswerNumber:
        payload_dictionary = cast(dict[str, object], self._dictionary(payload_source))
        answer_key = constants.QUIZ_FIELD_ANSWER
        answer = payload_dictionary.get(answer_key)
        if not isinstance(answer, int) or isinstance(answer, bool):
            raise ValueError(constants.ERROR_ANSWER_MUST_BE_INTEGER)
        return AnswerNumber.from_raw(answer)

    def _hint_text(self, payload_source: object) -> HintText | None:
        payload_dictionary = cast(dict[str, object], self._dictionary(payload_source))
        hint_key = constants.QUIZ_FIELD_HINT
        hint = payload_dictionary.get(hint_key)
        if hint is None:
            return None
        if not isinstance(hint, str) or not hint.strip():
            raise ValueError(constants.ERROR_HINT_MUST_BE_NON_EMPTY_STRING)
        return HintText.from_raw(hint)
