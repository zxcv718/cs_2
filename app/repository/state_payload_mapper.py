from typing import Any, Optional

import app.config.constants as c
from app.model.quiz import Quiz
from app.repository.quiz_payload_mapper import QuizPayloadMapper


# 게임 상태와 저장용 딕셔너리 사이 변환을 담당합니다.
class StatePayloadMapper:
    def __init__(self, quiz_mapper: Optional[QuizPayloadMapper] = None) -> None:
        self.quiz_mapper = quiz_mapper or QuizPayloadMapper()

    # 현재 상태를 JSON으로 저장 가능한 딕셔너리로 바꿉니다.
    def to_payload(
        self,
        quizzes: list[Quiz],
        best_score: Optional[int],
        history: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        if best_score is not None and not self._is_int(best_score):
            raise ValueError(c.ERROR_BEST_SCORE_MUST_BE_INTEGER_OR_NONE)

        payload: dict[str, Any] = {
            c.STATE_KEY_QUIZZES: [self.quiz_mapper.to_payload(quiz) for quiz in quizzes],
            c.STATE_KEY_BEST_SCORE: best_score,
        }

        if history is not None:
            payload[c.STATE_KEY_HISTORY] = [
                self._validate_and_copy_history_item(item) for item in history
            ]
        return payload

    # 저장된 딕셔너리를 프로그램에서 쓰는 상태로 복원합니다.
    def from_payload(self, data: Any) -> dict[str, Any]:
        if not isinstance(data, dict):
            raise ValueError(c.ERROR_STATE_MUST_BE_DICTIONARY)

        quizzes_data = data.get(c.STATE_KEY_QUIZZES)
        if not isinstance(quizzes_data, list):
            raise ValueError(c.ERROR_STATE_MUST_INCLUDE_QUIZZES)

        if c.STATE_KEY_BEST_SCORE not in data:
            raise ValueError(c.ERROR_STATE_MUST_INCLUDE_BEST_SCORE)

        best_score = data[c.STATE_KEY_BEST_SCORE]
        if best_score is not None and not self._is_int(best_score):
            raise ValueError(c.ERROR_BEST_SCORE_MUST_BE_INTEGER_OR_NONE)

        history_data = data.get(c.STATE_KEY_HISTORY, [])
        if not isinstance(history_data, list):
            raise ValueError(c.ERROR_HISTORY_MUST_BE_LIST)

        return {
            c.STATE_KEY_QUIZZES: [
                self.quiz_mapper.from_payload(item) for item in quizzes_data
            ],
            c.STATE_KEY_BEST_SCORE: best_score,
            c.STATE_KEY_HISTORY: [
                self._validate_and_copy_history_item(item) for item in history_data
            ],
        }

    # 플레이 기록 한 건의 형식이 맞는지 검사하고 복사본을 돌려줍니다.
    def _validate_and_copy_history_item(self, item: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(item, dict):
            raise ValueError(c.ERROR_HISTORY_ITEM_MUST_BE_DICTIONARY)

        played_at = item.get(c.HISTORY_FIELD_PLAYED_AT)
        if not isinstance(played_at, str) or not played_at.strip():
            raise ValueError(c.ERROR_PLAYED_AT_MUST_BE_NON_EMPTY_STRING)

        for key in (
            c.HISTORY_FIELD_TOTAL_QUESTIONS,
            c.HISTORY_FIELD_CORRECT_COUNT,
            c.HISTORY_FIELD_SCORE,
        ):
            value = item.get(key)
            if not self._is_int(value) or value < c.MINIMUM_SCORE:
                raise ValueError(c.ERROR_NON_NEGATIVE_INTEGER_TEMPLATE.format(key=key))

        # "맞힌 문제 수 > 전체 문제 수" 같은 모순된 기록은
        # 나중에 점수 계산이나 통계 처리에서 문제를 만들 수 있습니다.
        total_questions = item[c.HISTORY_FIELD_TOTAL_QUESTIONS]
        correct_count = item[c.HISTORY_FIELD_CORRECT_COUNT]
        if correct_count > total_questions:
            raise ValueError(c.ERROR_CORRECT_COUNT_EXCEEDS_TOTAL)

        hint_used_count = item.get(
            c.HISTORY_FIELD_HINT_USED_COUNT,
            c.INITIAL_HINT_USED_COUNT,
        )
        if not self._is_int(hint_used_count) or hint_used_count < c.MINIMUM_SCORE:
            raise ValueError(
                c.ERROR_NON_NEGATIVE_INTEGER_TEMPLATE.format(
                    key=c.HISTORY_FIELD_HINT_USED_COUNT
                )
            )
        if hint_used_count > total_questions:
            raise ValueError(c.ERROR_HINT_USED_COUNT_EXCEEDS_TOTAL)

        return {
            c.HISTORY_FIELD_PLAYED_AT: played_at,
            c.HISTORY_FIELD_TOTAL_QUESTIONS: total_questions,
            c.HISTORY_FIELD_CORRECT_COUNT: correct_count,
            c.HISTORY_FIELD_SCORE: item[c.HISTORY_FIELD_SCORE],
            c.HISTORY_FIELD_HINT_USED_COUNT: hint_used_count,
        }

    # bool은 int의 하위 타입이라서 따로 제외합니다.
    def _is_int(self, value: Any) -> bool:
        return isinstance(value, int) and not isinstance(value, bool)
