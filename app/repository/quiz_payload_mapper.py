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
        if not isinstance(item, dict):
            raise ValueError(constants.ERROR_QUIZ_ITEM_MUST_BE_DICTIONARY)

        question = item.get(constants.QUIZ_FIELD_QUESTION)
        if not isinstance(question, str) or not question.strip():
            raise ValueError(constants.ERROR_QUESTION_MUST_BE_NON_EMPTY_STRING)

        raw_choices = item.get(constants.QUIZ_FIELD_CHOICES)
        if not isinstance(raw_choices, list) or len(raw_choices) != constants.CHOICE_COUNT:
            raise ValueError(
                constants.ERROR_CHOICES_LENGTH_TEMPLATE.format(
                    choice_count=constants.CHOICE_COUNT
                )
            )

        choices: list[str] = []
        for choice in raw_choices:
            if not isinstance(choice, str) or not choice.strip():
                raise ValueError(constants.ERROR_CHOICE_MUST_BE_NON_EMPTY_STRING)
            choices.append(choice)

        answer = item.get(constants.QUIZ_FIELD_ANSWER)
        if not isinstance(answer, int) or isinstance(answer, bool):
            raise ValueError(constants.ERROR_ANSWER_MUST_BE_INTEGER)

        hint = item.get(constants.QUIZ_FIELD_HINT)
        if hint is not None and (not isinstance(hint, str) or not hint.strip()):
            raise ValueError(constants.ERROR_HINT_MUST_BE_NON_EMPTY_STRING)

        return self.quiz_factory.create(
            question=question,
            choices=choices,
            answer=answer,
            hint=hint,
        )
