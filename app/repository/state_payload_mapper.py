from dataclasses import dataclass, field
from typing import Optional, TypeGuard, cast

import app.config.constants as constants
from app.application.play.best_score_service import BestScore
from app.application.play.quiz_session_models import AnswerTally, QuizPerformance
from app.application.state.game_history import GameHistory, HistoryEntries
from app.application.state.game_record_book import GameRecordBook
from app.application.state.game_snapshot import GameSnapshot
from app.application.state.quiz_history_entry import QuizHistoryEntry, ScoredPerformance
from app.model.quiz_catalog import QuizCatalog, QuizItems
from app.repository.quiz_payload_mapper import QuizPayloadItem, QuizPayloadMapper
from app.service.quiz_metrics import CorrectAnswerCount, HintUsageCount, PlayedAt, QuestionCount, ScoreValue


@dataclass(frozen=True)
class QuizPayloadItems:
    values: tuple[QuizPayloadItem, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class HistoryPayloadItem:
    played_at: PlayedAt
    scored_performance: "HistoryScoredPerformance"


@dataclass(frozen=True)
class HistoryScoredPerformance:
    quiz_performance: QuizPerformance
    score_value: ScoreValue


@dataclass(frozen=True)
class HistoryPayloadItems:
    values: tuple[HistoryPayloadItem, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class StatePayload:
    quiz_payload_items: QuizPayloadItems
    content: "StatePayloadContent"


@dataclass(frozen=True)
class StatePayloadContent:
    best_score: BestScore
    history_payload_items: HistoryPayloadItems


class StatePayloadMapper:
    def __init__(self, quiz_mapper: Optional[QuizPayloadMapper] = None) -> None:
        self.quiz_mapper = quiz_mapper or QuizPayloadMapper()

    def to_state_payload(self, game_snapshot: GameSnapshot) -> StatePayload:
        quiz_mapper = self.quiz_mapper
        quiz_catalog = game_snapshot.quiz_catalog
        quiz_payload_items = tuple(
            quiz_mapper.to_payload_item(quiz) for quiz in quiz_catalog
        )
        game_record_book = game_snapshot.game_record_book
        history_payload_items = tuple(
            self._history_payload_item(entry) for entry in game_record_book.play_history
        )
        best_score = game_record_book.best_score
        payload_content = StatePayloadContent(
            best_score=best_score,
            history_payload_items=HistoryPayloadItems(history_payload_items),
        )
        return StatePayload(QuizPayloadItems(quiz_payload_items), payload_content)

    def from_state_payload(self, state_payload: StatePayload) -> GameSnapshot:
        quiz_mapper = self.quiz_mapper
        quiz_payloads = state_payload.quiz_payload_items
        quiz_payload_items = quiz_payloads.values
        quizzes = tuple(
            quiz_mapper.from_payload_item(payload_item)
            for payload_item in quiz_payload_items
        )
        payload_content = state_payload.content
        history_payloads = payload_content.history_payload_items
        history_payload_items = history_payloads.values
        history_entries = tuple(
            self._history_entry(payload_item)
            for payload_item in history_payload_items
        )
        quiz_catalog = QuizCatalog(QuizItems.from_iterable(quizzes))
        game_history = GameHistory(HistoryEntries.from_iterable(history_entries))
        game_record_book = GameRecordBook(payload_content.best_score, game_history)
        return GameSnapshot(quiz_catalog, game_record_book)

    def _state_payload(self, payload_source: object) -> StatePayload:
        quizzes_data = self._quizzes_data(payload_source)
        stored_best_score = self._stored_best_score(payload_source)
        history_data = self._history_data(payload_source)
        serialized_quiz_items = cast(list[object], quizzes_data)
        serialized_history_items = cast(list[object], history_data)
        quiz_mapper = self.quiz_mapper
        quiz_payload_items = tuple(
            quiz_mapper._payload_item(item)
            for item in serialized_quiz_items
        )
        history_payload_items = tuple(
            self._history_payload_item_from_dictionary(item)
            for item in serialized_history_items
        )
        best_score = self._best_score(stored_best_score)
        payload_content = StatePayloadContent(
            best_score=best_score,
            history_payload_items=HistoryPayloadItems(history_payload_items),
        )
        return StatePayload(QuizPayloadItems(quiz_payload_items), payload_content)

    def _payload_dictionary(self, state_payload: StatePayload) -> object:
        quiz_mapper = self.quiz_mapper
        quiz_payloads = state_payload.quiz_payload_items
        payload_content = state_payload.content
        history_payloads = payload_content.history_payload_items
        return {
            constants.STATE_KEY_QUIZZES: [
                quiz_mapper._payload_dictionary(payload_item)
                for payload_item in quiz_payloads.values
            ],
            constants.STATE_KEY_BEST_SCORE: self._stored_optional_score(payload_content.best_score),
            constants.STATE_KEY_HISTORY: [
                self._history_payload_dictionary(payload_item)
                for payload_item in history_payloads.values
            ],
        }

    def _history_payload_item(self, entry: QuizHistoryEntry) -> HistoryPayloadItem:
        played_at = entry.played_at
        scored_performance = entry.scored_performance
        quiz_performance = scored_performance.quiz_performance
        score_value = scored_performance.score_value
        scored_performance = HistoryScoredPerformance(quiz_performance, score_value)
        return HistoryPayloadItem(played_at, scored_performance)

    def _history_entry(self, payload_item: HistoryPayloadItem) -> QuizHistoryEntry:
        payload_scored_performance = payload_item.scored_performance
        scored_performance = ScoredPerformance(
            payload_scored_performance.quiz_performance,
            payload_scored_performance.score_value,
        )
        return QuizHistoryEntry(
            payload_item.played_at,
            scored_performance,
        )

    def _history_payload_item_from_dictionary(
        self,
        payload_source: object,
    ) -> HistoryPayloadItem:
        history_dictionary = cast(dict[str, object], self._history_dictionary(payload_source))
        played_at = self._played_at(history_dictionary)
        total_questions = self._required_count(history_dictionary, constants.HISTORY_FIELD_TOTAL_QUESTIONS)
        correct_count = self._required_count(history_dictionary, constants.HISTORY_FIELD_CORRECT_COUNT)
        score = self._required_count(history_dictionary, constants.HISTORY_FIELD_SCORE)
        if correct_count > total_questions:
            raise ValueError(constants.ERROR_CORRECT_COUNT_EXCEEDS_TOTAL)

        hint_used_count = self._hint_used_count(history_dictionary)
        if hint_used_count > total_questions:
            raise ValueError(constants.ERROR_HINT_USED_COUNT_EXCEEDS_TOTAL)

        quiz_performance = QuizPerformance(
            QuestionCount(total_questions),
            AnswerTally(
                CorrectAnswerCount(correct_count),
                HintUsageCount(hint_used_count),
            ),
        )
        scored_performance = HistoryScoredPerformance(
            quiz_performance=quiz_performance,
            score_value=ScoreValue(score),
        )
        return HistoryPayloadItem(played_at, scored_performance)

    def _history_payload_dictionary(
        self,
        payload_item: HistoryPayloadItem,
    ) -> object:
        scored_performance = payload_item.scored_performance
        quiz_performance = scored_performance.quiz_performance
        answer_tally = quiz_performance.answer_tally
        return {
            constants.HISTORY_FIELD_PLAYED_AT: str(payload_item.played_at),
            constants.HISTORY_FIELD_TOTAL_QUESTIONS: int(quiz_performance.total_questions),
            constants.HISTORY_FIELD_CORRECT_COUNT: int(answer_tally.correct_answers),
            constants.HISTORY_FIELD_SCORE: int(scored_performance.score_value),
            constants.HISTORY_FIELD_HINT_USED_COUNT: int(answer_tally.hint_usages),
        }

    def _quizzes_data(self, payload_source: object) -> object:
        state_dictionary = cast(dict[str, object], self._state_dictionary(payload_source))
        quizzes_key = constants.STATE_KEY_QUIZZES
        quizzes_data = state_dictionary.get(quizzes_key)
        if not isinstance(quizzes_data, list):
            raise ValueError(constants.ERROR_STATE_MUST_INCLUDE_QUIZZES)
        return quizzes_data

    def _stored_best_score(self, payload_source: object) -> int | None:
        state_dictionary = cast(dict[str, object], self._state_dictionary(payload_source))
        best_score_key = constants.STATE_KEY_BEST_SCORE
        if best_score_key not in state_dictionary:
            raise ValueError(constants.ERROR_STATE_MUST_INCLUDE_BEST_SCORE)
        stored_best_score = state_dictionary[best_score_key]
        if stored_best_score is not None and not self._is_int(stored_best_score):
            raise ValueError(constants.ERROR_BEST_SCORE_MUST_BE_INTEGER_OR_NONE)
        return cast(int | None, stored_best_score)

    def _history_data(self, payload_source: object) -> object:
        state_dictionary = cast(dict[str, object], self._state_dictionary(payload_source))
        history_key = constants.STATE_KEY_HISTORY
        history_data = state_dictionary.get(history_key, [])
        if not isinstance(history_data, list):
            raise ValueError(constants.ERROR_HISTORY_MUST_BE_LIST)
        return history_data

    def _best_score(self, stored_best_score: int | None) -> BestScore:
        return BestScore.from_optional_int(stored_best_score)

    def _stored_optional_score(self, best_score: BestScore) -> int | None:
        score_value = best_score.score_value
        if score_value is None:
            return None
        return int(score_value)

    def _is_int(self, value: object) -> TypeGuard[int]:
        return isinstance(value, int) and not isinstance(value, bool)

    def _played_at(self, payload_source: object) -> PlayedAt:
        history_dictionary = cast(dict[str, object], self._history_dictionary(payload_source))
        played_at_key = constants.HISTORY_FIELD_PLAYED_AT
        played_at_text = history_dictionary.get(played_at_key)
        if not isinstance(played_at_text, str):
            raise ValueError(constants.ERROR_PLAYED_AT_MUST_BE_NON_EMPTY_STRING)
        return PlayedAt.from_raw(played_at_text)

    def _required_count(self, payload_source: object, key: str) -> int:
        history_dictionary = cast(dict[str, object], self._history_dictionary(payload_source))
        value = history_dictionary.get(key)
        if not self._is_int(value) or value < constants.MINIMUM_SCORE:
            error_template = constants.ERROR_NON_NEGATIVE_INTEGER_TEMPLATE
            raise ValueError(error_template.format(key=key))
        return cast(int, value)

    def _hint_used_count(self, payload_source: object) -> int:
        history_dictionary = cast(dict[str, object], self._history_dictionary(payload_source))
        key = constants.HISTORY_FIELD_HINT_USED_COUNT
        default_value = constants.INITIAL_HINT_USED_COUNT
        hint_used_count = history_dictionary.get(key, default_value)
        if not self._is_int(hint_used_count) or hint_used_count < constants.MINIMUM_SCORE:
            error_template = constants.ERROR_NON_NEGATIVE_INTEGER_TEMPLATE
            raise ValueError(error_template.format(key=key))
        return hint_used_count

    def _state_dictionary(self, payload_source: object) -> object:
        if isinstance(payload_source, dict):
            return cast(dict[str, object], payload_source)
        raise ValueError(constants.ERROR_STATE_MUST_BE_DICTIONARY)

    def _history_dictionary(self, payload_source: object) -> object:
        if isinstance(payload_source, dict):
            return cast(dict[str, object], payload_source)
        raise ValueError(constants.ERROR_HISTORY_ITEM_MUST_BE_DICTIONARY)
