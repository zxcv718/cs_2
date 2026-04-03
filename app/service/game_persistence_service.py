from typing import Any, Optional

import app.config.constants as c
from app.model.quiz import Quiz
from app.service.game_runtime_state import GameRuntimeState
from app.service.game_state_service import GameStateService
from app.ui.console_ui import ConsoleUI


class GamePersistenceService:
    def __init__(self, state_service: GameStateService, ui: ConsoleUI) -> None:
        self.state_service = state_service
        self.ui = ui

    def save_runtime_state(self, runtime_state: GameRuntimeState) -> None:
        self.save_state_values(
            runtime_state.quizzes,
            runtime_state.best_score,
            runtime_state.history,
        )

    def save_state_values(
        self,
        quizzes: list[Quiz],
        best_score: Optional[int],
        history: list[dict[str, Any]],
    ) -> None:
        try:
            self.state_service.save_state(quizzes, best_score, history)
        except OSError:
            self.ui.show_error(c.ERROR_STATE_SAVE)
