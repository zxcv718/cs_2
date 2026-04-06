from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import app.config.constants as constants
from app.model.quiz import Quiz
from app.model.quiz_catalog import QuizCatalog
from app.service.game_history import GameHistory
from app.service.game_lifecycle import GameLifecycle
from app.service.game_record_book import GameRecordBook
from app.service.quiz_metrics import ScoreValue


@dataclass
class GameRuntimeState:
    quiz_catalog: QuizCatalog = field(default_factory=QuizCatalog)
    game_lifecycle: GameLifecycle = field(default_factory=GameLifecycle.create_uninitialized)

    def restore(
        self,
        quizzes: list[Quiz],
        best_score: int | None,
        history: list[dict[str, Any]],
    ) -> None:
        quiz_catalog = QuizCatalog.from_items(quizzes)
        history_entries = GameHistory.from_entries(history)
        wrapped_best_score = self._wrapped_score(best_score)
        record_book = GameRecordBook(wrapped_best_score, history_entries)
        self.quiz_catalog = quiz_catalog
        self.game_lifecycle = GameLifecycle(record_book, True)

    def apply_loaded_state(self, state: dict[str, Any]) -> None:
        history_key = constants.STATE_KEY_HISTORY
        self.restore(
            state[constants.STATE_KEY_QUIZZES],
            state[constants.STATE_KEY_BEST_SCORE],
            state.get(history_key, []),
        )

    def record_play_result(
        self,
        best_score: ScoreValue | None,
        history_entry: dict[str, Any],
    ) -> None:
        game_lifecycle = self.game_lifecycle
        record_book = game_lifecycle.record_book
        record_book.record(best_score, history_entry)

    def _wrapped_score(self, best_score: int | None) -> ScoreValue | None:
        if best_score is None:
            return None
        return ScoreValue(best_score)
