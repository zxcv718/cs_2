from typing import Any, Optional

import app.config.constants as constants
from app.model.quiz import Quiz
from app.model.quiz_factory import QuizFactory


# Quiz와 저장용 딕셔너리 사이 변환을 담당합니다.
class QuizPayloadMapper:
    def __init__(self, quiz_factory: Optional[QuizFactory] = None) -> None:
        self.quiz_factory = quiz_factory or QuizFactory()

    # Quiz 객체를 저장 가능한 딕셔너리로 바꿉니다.
    def to_payload(self, quiz: Quiz) -> dict[str, Any]:
        if not isinstance(quiz, Quiz):
            raise ValueError(constants.ERROR_QUIZ_MUST_BE_INSTANCE)
        return quiz.payload_item()

    # 저장된 딕셔너리를 Quiz 객체로 복원합니다.
    def from_payload(self, item: dict[str, Any]) -> Quiz:
        valid_item = self._dictionary(item)
        question = self._question(valid_item)
        choices = self._choices(valid_item)
        answer = self._answer(valid_item)
        hint = self._hint(valid_item)
        quiz_factory = self.quiz_factory
        return quiz_factory.create(
            question=question,
            choices=choices,
            answer=answer,
            hint=hint,
        )

    def _dictionary(self, item: dict[str, Any]) -> dict[str, Any]:
        if isinstance(item, dict):
            return item
        raise ValueError(constants.ERROR_QUIZ_ITEM_MUST_BE_DICTIONARY)

    def _question(self, item: dict[str, Any]) -> str:
        question_key = constants.QUIZ_FIELD_QUESTION
        question = item.get(question_key)
        if not isinstance(question, str) or not question.strip():
            raise ValueError(constants.ERROR_QUESTION_MUST_BE_NON_EMPTY_STRING)
        return question

    def _choices(self, item: dict[str, Any]) -> list[str]:
        choices_key = constants.QUIZ_FIELD_CHOICES
        raw_choices = item.get(choices_key)
        if not isinstance(raw_choices, list) or len(raw_choices) != constants.CHOICE_COUNT:
            error_template = constants.ERROR_CHOICES_LENGTH_TEMPLATE
            raise ValueError(error_template.format(choice_count=constants.CHOICE_COUNT))
        return [self._choice(choice) for choice in raw_choices]

    def _choice(self, choice: Any) -> str:
        if not isinstance(choice, str) or not choice.strip():
            raise ValueError(constants.ERROR_CHOICE_MUST_BE_NON_EMPTY_STRING)
        return choice

    def _answer(self, item: dict[str, Any]) -> int:
        answer_key = constants.QUIZ_FIELD_ANSWER
        answer = item.get(answer_key)
        if not isinstance(answer, int) or isinstance(answer, bool):
            raise ValueError(constants.ERROR_ANSWER_MUST_BE_INTEGER)
        return answer

    def _hint(self, item: dict[str, Any]) -> str | None:
        hint_key = constants.QUIZ_FIELD_HINT
        hint = item.get(hint_key)
        if hint is None:
            return None
        if not isinstance(hint, str) or not hint.strip():
            raise ValueError(constants.ERROR_HINT_MUST_BE_NON_EMPTY_STRING)
        return hint
