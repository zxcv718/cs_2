from typing import Any

import app.config.constants as c
from app.model.quiz import Quiz


# Quiz와 저장용 딕셔너리 사이 변환을 담당합니다.
class QuizPayloadMapper:
    # Quiz 객체를 저장 가능한 딕셔너리로 바꿉니다.
    def to_payload(self, quiz: Quiz) -> dict[str, Any]:
        if not isinstance(quiz, Quiz):
            raise ValueError(c.ERROR_QUIZ_MUST_BE_INSTANCE)

        item = {
            c.QUIZ_FIELD_QUESTION: quiz.question,
            c.QUIZ_FIELD_CHOICES: list(quiz.choices),
            c.QUIZ_FIELD_ANSWER: quiz.answer,
        }
        if quiz.has_hint():
            item[c.QUIZ_FIELD_HINT] = quiz.get_hint_text()
        return item

    # 저장된 딕셔너리를 Quiz 객체로 복원합니다.
    def from_payload(self, item: dict[str, Any]) -> Quiz:
        if not isinstance(item, dict):
            raise ValueError(c.ERROR_QUIZ_ITEM_MUST_BE_DICTIONARY)

        hint = item.get(c.QUIZ_FIELD_HINT)
        if hint is not None and (not isinstance(hint, str) or not hint.strip()):
            raise ValueError(c.ERROR_HINT_MUST_BE_NON_EMPTY_STRING)

        return Quiz(
            question=item.get(c.QUIZ_FIELD_QUESTION),
            choices=item.get(c.QUIZ_FIELD_CHOICES),
            answer=item.get(c.QUIZ_FIELD_ANSWER),
            hint=hint,
        )
