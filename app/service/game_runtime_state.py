from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional

import app.config.constants as c
from app.model.quiz import Quiz
from app.model.quiz_catalog import QuizCatalog
from app.service.game_history import GameHistory
from app.service.game_lifecycle import GameLifecycle
from app.service.game_record_book import GameRecordBook

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
        best_score: Optional[int],
        history: list[dict[str, Any]],
    ) -> None:
        self.quiz_catalog = QuizCatalog.from_items(quizzes)
        history_entries = GameHistory.from_entries(history)
        record_book = GameRecordBook(best_score, history_entries)
        self.game_lifecycle = GameLifecycle(record_book, True)

    def apply_loaded_state(self, state: dict[str, Any]) -> None:
        self.restore(
            state[c.STATE_KEY_QUIZZES],
            state[c.STATE_KEY_BEST_SCORE],
            state.get(c.STATE_KEY_HISTORY, []),
        )

    def record_play_result(
        self,
        best_score: Optional[int],
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
            self.quiz_catalog.persistable_items(),
            self.game_lifecycle.record_book.best_score,
            self.game_lifecycle.record_book.history.persistable_entries(),
        )

    def show_best_score_on(self, console_interface: ConsoleUI) -> None:
        console_interface.show_best_score(self.game_lifecycle.record_book.best_score)
