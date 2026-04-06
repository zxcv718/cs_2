from typing import Any, Optional

import app.config.constants as constants
from app.model.quiz import Quiz
from app.service.game_runtime_state import GameRuntimeState
from app.service.game_state_service import GameStateService
from app.service.quiz_metrics import ScoreValue
from app.console_interface import ConsoleInterface


class GamePersistenceService:
    def __init__(
        self,
        state_service: GameStateService,
        console_interface: ConsoleInterface,
    ) -> None:
        self.state_service = state_service
        self.console_interface = console_interface

    def save_runtime_state(self, runtime_state: GameRuntimeState) -> None:
        state_service = self.state_service
        console_interface = self.console_interface
        try:
            quizzes = list(runtime_state.quiz_catalog)
            game_lifecycle = runtime_state.game_lifecycle
            record_book = game_lifecycle.record_book
            best_score = self._score_value_or_none(record_book.best_score)
            history = list(record_book.history)
            state_service.save_state(quizzes, best_score, history)
        except OSError:
            console_interface.show_error(constants.ERROR_STATE_SAVE)
            return

    def save_state_values(
        self,
        quizzes: list[Quiz],
        best_score: Optional[int],
        history: list[dict[str, Any]],
    ) -> None:
        state_service = self.state_service
        console_interface = self.console_interface
        try:
            state_service.save_state(quizzes, best_score, history)
        except OSError:
            console_interface.show_error(constants.ERROR_STATE_SAVE)

    def _score_value_or_none(self, score_value: ScoreValue | None) -> int | None:
        if score_value is None:
            return None
        return int(score_value)
