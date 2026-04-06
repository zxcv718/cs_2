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

        quiz_mapper = self.quiz_mapper
        payload: dict[str, Any] = {
            constants.STATE_KEY_QUIZZES: [
                quiz_mapper.to_payload(quiz) for quiz in quizzes
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

        quizzes_key = constants.STATE_KEY_QUIZZES
        quizzes_data = data.get(quizzes_key)
        if not isinstance(quizzes_data, list):
            raise ValueError(constants.ERROR_STATE_MUST_INCLUDE_QUIZZES)

        best_score_key = constants.STATE_KEY_BEST_SCORE
        if best_score_key not in data:
            raise ValueError(constants.ERROR_STATE_MUST_INCLUDE_BEST_SCORE)

        best_score = data[best_score_key]
        if best_score is not None and not self._is_int(best_score):
            raise ValueError(constants.ERROR_BEST_SCORE_MUST_BE_INTEGER_OR_NONE)

        history_key = constants.STATE_KEY_HISTORY
        history_data = data.get(history_key, [])
        if not isinstance(history_data, list):
            raise ValueError(constants.ERROR_HISTORY_MUST_BE_LIST)

        quiz_mapper = self.quiz_mapper
        return {
            constants.STATE_KEY_QUIZZES: [
                quiz_mapper.from_payload(item) for item in quizzes_data
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

        played_at = self._played_at(item)
        total_questions = self._required_count(item, constants.HISTORY_FIELD_TOTAL_QUESTIONS)
        correct_count = self._required_count(item, constants.HISTORY_FIELD_CORRECT_COUNT)
        score = self._required_count(item, constants.HISTORY_FIELD_SCORE)
        if correct_count > total_questions:
            raise ValueError(constants.ERROR_CORRECT_COUNT_EXCEEDS_TOTAL)

        hint_used_count = self._hint_used_count(item)
        if hint_used_count > total_questions:
            raise ValueError(constants.ERROR_HINT_USED_COUNT_EXCEEDS_TOTAL)

        return {
            constants.HISTORY_FIELD_PLAYED_AT: str(played_at),
            constants.HISTORY_FIELD_TOTAL_QUESTIONS: total_questions,
            constants.HISTORY_FIELD_CORRECT_COUNT: correct_count,
            constants.HISTORY_FIELD_SCORE: score,
            constants.HISTORY_FIELD_HINT_USED_COUNT: hint_used_count,
        }

    # bool은 int의 하위 타입이라서 따로 제외합니다.
    def _is_int(self, value: Any) -> TypeGuard[int]:
        return isinstance(value, int) and not isinstance(value, bool)

    def _played_at(self, item: dict[str, Any]) -> PlayedAt:
        played_at_key = constants.HISTORY_FIELD_PLAYED_AT
        raw_played_at = item.get(played_at_key)
        if not isinstance(raw_played_at, str):
            raise ValueError(constants.ERROR_PLAYED_AT_MUST_BE_NON_EMPTY_STRING)
        return PlayedAt.from_raw(raw_played_at)

    def _required_count(self, item: dict[str, Any], key: str) -> int:
        value = item.get(key)
        if not self._is_int(value) or value < constants.MINIMUM_SCORE:
            error_template = constants.ERROR_NON_NEGATIVE_INTEGER_TEMPLATE
            raise ValueError(error_template.format(key=key))
        return cast(int, value)

    def _hint_used_count(self, item: dict[str, Any]) -> int:
        key = constants.HISTORY_FIELD_HINT_USED_COUNT
        default_value = constants.INITIAL_HINT_USED_COUNT
        hint_used_count = item.get(key, default_value)
        if not self._is_int(hint_used_count) or hint_used_count < constants.MINIMUM_SCORE:
            error_template = constants.ERROR_NON_NEGATIVE_INTEGER_TEMPLATE
            raise ValueError(error_template.format(key=key))
        return hint_used_count
