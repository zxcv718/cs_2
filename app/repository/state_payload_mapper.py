from typing import Any, Optional, TypeGuard, cast

import app.config.constants as constants
from app.application.play.best_score_service import BestScore
from app.application.play.quiz_session_models import AnswerTally, QuizPerformance
from app.application.state.game_history import GameHistory
from app.application.state.game_record_book import GameRecordBook
from app.application.state.game_snapshot import GameSnapshot
from app.application.state.quiz_history_entry import QuizHistoryEntry
from app.model.quiz_catalog import QuizCatalog
from app.repository.quiz_payload_mapper import QuizPayloadMapper
from app.service.quiz_metrics import CorrectAnswerCount, HintUsageCount, PlayedAt, QuestionCount, ScoreValue


class StatePayloadMapper:
    def __init__(self, quiz_mapper: Optional[QuizPayloadMapper] = None) -> None:
        self.quiz_mapper = quiz_mapper or QuizPayloadMapper()

    def to_payload(self, game_snapshot: GameSnapshot) -> dict[str, Any]:
        quiz_mapper = self.quiz_mapper
        quiz_catalog = game_snapshot.quiz_catalog()
        game_record_book = game_snapshot.game_record_book()
        best_score = game_record_book.current_best_score()
        play_history = game_record_book.play_history()
        payload: dict[str, Any] = {
            constants.STATE_KEY_QUIZZES: [
                quiz_mapper.to_payload(quiz) for quiz in quiz_catalog
            ],
            constants.STATE_KEY_BEST_SCORE: best_score.to_optional_int(),
            constants.STATE_KEY_HISTORY: [
                self._history_item_dictionary(entry) for entry in play_history
            ],
        }
        return payload

    def from_payload(self, data: Any) -> GameSnapshot:
        if not isinstance(data, dict):
            raise ValueError(constants.ERROR_STATE_MUST_BE_DICTIONARY)

        quizzes_key = constants.STATE_KEY_QUIZZES
        quizzes_data = data.get(quizzes_key)
        if not isinstance(quizzes_data, list):
            raise ValueError(constants.ERROR_STATE_MUST_INCLUDE_QUIZZES)

        best_score_key = constants.STATE_KEY_BEST_SCORE
        if best_score_key not in data:
            raise ValueError(constants.ERROR_STATE_MUST_INCLUDE_BEST_SCORE)

        raw_best_score = data[best_score_key]
        if raw_best_score is not None and not self._is_int(raw_best_score):
            raise ValueError(constants.ERROR_BEST_SCORE_MUST_BE_INTEGER_OR_NONE)

        history_key = constants.STATE_KEY_HISTORY
        history_data = data.get(history_key, [])
        if not isinstance(history_data, list):
            raise ValueError(constants.ERROR_HISTORY_MUST_BE_LIST)

        quiz_mapper = self.quiz_mapper
        quiz_catalog = QuizCatalog.from_items(
            [quiz_mapper.from_payload(item) for item in quizzes_data]
        )
        game_record_book = GameRecordBook(
            BestScore.from_optional_int(cast(int | None, raw_best_score)),
            GameHistory.from_entries(
                [self._history_entry(item) for item in history_data]
            ),
        )
        return GameSnapshot(quiz_catalog, game_record_book)

    def _history_item_dictionary(self, entry: QuizHistoryEntry) -> dict[str, Any]:
        return {
            constants.HISTORY_FIELD_PLAYED_AT: str(entry.played_at()),
            constants.HISTORY_FIELD_TOTAL_QUESTIONS: int(entry.question_count()),
            constants.HISTORY_FIELD_CORRECT_COUNT: int(entry.correct_answers()),
            constants.HISTORY_FIELD_SCORE: int(entry.score_value()),
            constants.HISTORY_FIELD_HINT_USED_COUNT: int(entry.hint_usages()),
        }

    def _history_entry(self, item: dict[str, Any]) -> QuizHistoryEntry:
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

        quiz_performance = QuizPerformance(
            QuestionCount(total_questions),
            AnswerTally(
                CorrectAnswerCount(correct_count),
                HintUsageCount(hint_used_count),
            ),
        )
        return QuizHistoryEntry.restore(
            played_at,
            quiz_performance,
            ScoreValue(score),
        )

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
