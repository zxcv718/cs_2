from typing import Any, Optional, TypeGuard, cast

import app.config.constants as constants
from app.model.quiz import Quiz
from app.repository.quiz_payload_mapper import QuizPayloadMapper
from app.service.quiz_metrics import PlayedAt


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
            raise ValueError(constants.ERROR_BEST_SCORE_MUST_BE_INTEGER_OR_NONE)

        payload: dict[str, Any] = {
            constants.STATE_KEY_QUIZZES: [
                self.quiz_mapper.to_payload(quiz) for quiz in quizzes
            ],
            constants.STATE_KEY_BEST_SCORE: best_score,
        }

        if history is not None:
            payload[constants.STATE_KEY_HISTORY] = [
                self._validate_and_copy_history_item(item) for item in history
            ]
        return payload

    # 저장된 딕셔너리를 프로그램에서 쓰는 상태로 복원합니다.
    def from_payload(self, data: Any) -> dict[str, Any]:
        if not isinstance(data, dict):
            raise ValueError(constants.ERROR_STATE_MUST_BE_DICTIONARY)

        quizzes_data = data.get(constants.STATE_KEY_QUIZZES)
        if not isinstance(quizzes_data, list):
            raise ValueError(constants.ERROR_STATE_MUST_INCLUDE_QUIZZES)

        if constants.STATE_KEY_BEST_SCORE not in data:
            raise ValueError(constants.ERROR_STATE_MUST_INCLUDE_BEST_SCORE)

        best_score = data[constants.STATE_KEY_BEST_SCORE]
        if best_score is not None and not self._is_int(best_score):
            raise ValueError(constants.ERROR_BEST_SCORE_MUST_BE_INTEGER_OR_NONE)

        history_data = data.get(constants.STATE_KEY_HISTORY, [])
        if not isinstance(history_data, list):
            raise ValueError(constants.ERROR_HISTORY_MUST_BE_LIST)

        return {
            constants.STATE_KEY_QUIZZES: [
                self.quiz_mapper.from_payload(item) for item in quizzes_data
            ],
            constants.STATE_KEY_BEST_SCORE: best_score,
            constants.STATE_KEY_HISTORY: [
                self._validate_and_copy_history_item(item) for item in history_data
            ],
        }

    # 플레이 기록 한 건의 형식이 맞는지 검사하고 복사본을 돌려줍니다.
    def _validate_and_copy_history_item(self, item: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(item, dict):
            raise ValueError(constants.ERROR_HISTORY_ITEM_MUST_BE_DICTIONARY)

        raw_played_at = item.get(constants.HISTORY_FIELD_PLAYED_AT)
        if not isinstance(raw_played_at, str):
            raise ValueError(constants.ERROR_PLAYED_AT_MUST_BE_NON_EMPTY_STRING)
        played_at = PlayedAt.from_raw(raw_played_at)

        for key in (
            constants.HISTORY_FIELD_TOTAL_QUESTIONS,
            constants.HISTORY_FIELD_CORRECT_COUNT,
            constants.HISTORY_FIELD_SCORE,
        ):
            value = item.get(key)
            if not self._is_int(value) or value < constants.MINIMUM_SCORE:
                raise ValueError(
                    constants.ERROR_NON_NEGATIVE_INTEGER_TEMPLATE.format(key=key)
                )

        # "맞힌 문제 수 > 전체 문제 수" 같은 모순된 기록은
        # 나중에 점수 계산이나 통계 처리에서 문제를 만들 수 있습니다.
        total_questions = cast(int, item[constants.HISTORY_FIELD_TOTAL_QUESTIONS])
        correct_count = cast(int, item[constants.HISTORY_FIELD_CORRECT_COUNT])
        if correct_count > total_questions:
            raise ValueError(constants.ERROR_CORRECT_COUNT_EXCEEDS_TOTAL)

        hint_used_count = item.get(
            constants.HISTORY_FIELD_HINT_USED_COUNT,
            constants.INITIAL_HINT_USED_COUNT,
        )
        if not self._is_int(hint_used_count) or hint_used_count < constants.MINIMUM_SCORE:
            raise ValueError(
                constants.ERROR_NON_NEGATIVE_INTEGER_TEMPLATE.format(
                    key=constants.HISTORY_FIELD_HINT_USED_COUNT
                )
            )
        if hint_used_count > total_questions:
            raise ValueError(constants.ERROR_HINT_USED_COUNT_EXCEEDS_TOTAL)

        return {
            constants.HISTORY_FIELD_PLAYED_AT: str(played_at),
            constants.HISTORY_FIELD_TOTAL_QUESTIONS: total_questions,
            constants.HISTORY_FIELD_CORRECT_COUNT: correct_count,
            constants.HISTORY_FIELD_SCORE: item[constants.HISTORY_FIELD_SCORE],
            constants.HISTORY_FIELD_HINT_USED_COUNT: hint_used_count,
        }

    # bool은 int의 하위 타입이라서 따로 제외합니다.
    def _is_int(self, value: Any) -> TypeGuard[int]:
        return isinstance(value, int) and not isinstance(value, bool)
