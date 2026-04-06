from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import app.config.constants as constants
from app.model.quiz import Quiz
from app.model.quiz_catalog import QuizCatalog
from app.service.game_history import GameHistory
from app.service.game_lifecycle import GameLifecycle
from app.service.game_record_book import GameRecordBook
from app.service.quiz_metrics import ScoreValue

if TYPE_CHECKING:
    from app.service.game_bootstrap_service import GameBootstrapService
    from app.service.game_state_service import GameStateService
    from app.ui.console_ui import ConsoleUI


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
        self.quiz_catalog = QuizCatalog.from_items(quizzes)
        history_entries = GameHistory.from_entries(history)
        wrapped_best_score = None if best_score is None else ScoreValue(best_score)
        record_book = GameRecordBook(wrapped_best_score, history_entries)
        self.game_lifecycle = GameLifecycle(record_book, True)

    def apply_loaded_state(self, state: dict[str, Any]) -> None:
        self.restore(
            state[constants.STATE_KEY_QUIZZES],
            state[constants.STATE_KEY_BEST_SCORE],
            state.get(constants.STATE_KEY_HISTORY, []),
        )

    def record_play_result(
        self,
        best_score: ScoreValue | None,
        history_entry: dict[str, Any],
    ) -> None:
        self.game_lifecycle.record_book.record(best_score, history_entry)

    def initialize_with(
        self,
        game_bootstrap_service: GameBootstrapService,
        console_interface: ConsoleUI,
    ) -> None:
        if self.game_lifecycle.initialized:
            return
        game_bootstrap_service.initialize(self, console_interface)

    def save_with(self, game_state_service: GameStateService) -> None:
        game_state_service.save_state(
            list(self.quiz_catalog),
            _score_value_or_none(self.game_lifecycle.record_book.best_score),
            list(self.game_lifecycle.record_book.history),
        )

    def show_best_score_on(self, console_interface: ConsoleUI) -> None:
        console_interface.display_best_score(
            _score_value_or_none(self.game_lifecycle.record_book.best_score)
        )


def _score_value_or_none(score_value: ScoreValue | None) -> int | None:
    if score_value is None:
        return None
    return int(score_value)
