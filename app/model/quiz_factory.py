from typing import Optional

from app.model.quiz import Quiz
from app.model.quiz_components import AnswerNumber, ChoiceSet, HintText, QuestionText


class QuizFactory:
    # Quiz 생성에 필요한 입력 검증과 정규화를 한곳에 모읍니다.
    def create(
        self,
        question: str,
        choices: list[str],
        answer: int,
        hint: Optional[str] = None,
    ) -> Quiz:
        question_text = QuestionText.from_raw(question)
        choice_set = ChoiceSet.from_raw(choices)
        answer_number = AnswerNumber.from_raw(answer)
        hint_text = HintText.from_raw(hint)

        return Quiz(
            question_text.value,
            choice_set.values,
            answer_number.value,
            None if hint_text is None else hint_text.value,
        )
