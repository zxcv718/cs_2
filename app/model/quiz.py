import app.config.constants as c
from typing import Optional


# 퀴즈 한 문제를 표현하는 클래스입니다.
class Quiz:
    def __init__(
        self,
        question: str,
        choices: list[str],
        answer: int,
        hint: Optional[str] = None,
    ) -> None:
        # 입력값을 바로 저장하지 않고 먼저 검증합니다.
        self.question = self._validate_question(question)
        self.choices = self._validate_choices(choices)
        self.answer = self._validate_answer(answer)
        self.hint = self._validate_hint(hint)

    # 사용자가 고른 번호가 정답인지 확인합니다.
    def is_correct(self, user_answer: int) -> bool:
        return user_answer == self.answer

    # 이 문제에 힌트가 있는지 알려줍니다.
    def has_hint(self) -> bool:
        return self.hint is not None

    # 힌트가 없으면 빈 문자열을 돌려줍니다.
    def get_hint_text(self) -> str:
        return self.hint or c.EMPTY_TEXT

    # 문제 문장이 문자열인지, 비어 있지 않은지 검사합니다.
    def _validate_question(self, question: str) -> str:
        if not isinstance(question, str):
            raise ValueError(c.ERROR_QUESTION_MUST_BE_STRING)
        normalized = question.strip()
        if not normalized:
            raise ValueError(c.ERROR_QUESTION_MUST_NOT_BE_EMPTY)
        return normalized

    # 선택지가 4개인지, 각 항목이 비어 있지 않은지 검사합니다.
    def _validate_choices(self, choices: list[str]) -> list[str]:
        if not isinstance(choices, list) or len(choices) != c.CHOICE_COUNT:
            raise ValueError(
                c.ERROR_CHOICES_LENGTH_TEMPLATE.format(choice_count=c.CHOICE_COUNT)
            )

        normalized_choices: list[str] = []
        for choice in choices:
            if not isinstance(choice, str):
                raise ValueError(c.ERROR_CHOICE_MUST_BE_STRING)
            # 앞뒤 공백은 제거해서 저장합니다.
            normalized = choice.strip()
            if not normalized:
                raise ValueError(c.ERROR_CHOICE_MUST_NOT_BE_EMPTY)
            normalized_choices.append(normalized)
        return normalized_choices

    # 정답 번호가 1~4 범위에 있는지 검사합니다.
    def _validate_answer(self, answer: int) -> int:
        if not isinstance(answer, int) or isinstance(answer, bool):
            raise ValueError(c.ERROR_ANSWER_MUST_BE_INTEGER)
        if answer < c.MIN_ANSWER or answer > c.MAX_ANSWER:
            raise ValueError(
                c.ERROR_ANSWER_RANGE_TEMPLATE.format(
                    min_answer=c.MIN_ANSWER,
                    max_answer=c.MAX_ANSWER,
                )
            )
        return answer

    # 힌트는 문자열 또는 None만 허용합니다.
    def _validate_hint(self, hint: Optional[str]) -> Optional[str]:
        if hint is None:
            return None
        if not isinstance(hint, str):
            raise ValueError(c.ERROR_HINT_MUST_BE_STRING_OR_NONE)
        # 공백만 있는 힌트는 없는 것으로 처리합니다.
        normalized = hint.strip()
        if not normalized:
            return None
        return normalized
