import app.config.constants as c
from typing import Optional


# 퀴즈 한 문제의 관련 동작만 표현하는 클래스
class Quiz:
    def __init__(
        self,
        question: str,
        choices: tuple[str, ...],
        answer: int,
        hint: Optional[str] = None,
    ) -> None:
        self._question = question
        self._choices = choices
        self._answer = answer
        self._hint = hint

    def is_correct(self, user_answer: int) -> bool:
        return user_answer == self._answer

    def has_hint(self) -> bool:
        return self._hint is not None

    def question_text(self) -> str:
        return self._question

    def choice_texts(self) -> tuple[str, ...]:
        return self._choices

    def answer_number(self) -> int:
        return self._answer

    def hint_text(self) -> str:
        return self._hint or c.EMPTY_TEXT

    def raw_hint(self) -> Optional[str]:
        return self._hint

    def correct_choice_text(self) -> str:
        return self._choices[self._answer - c.DISPLAY_INDEX_START]
