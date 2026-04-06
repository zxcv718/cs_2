from typing import Any, Optional

import app.config.constants as c
from app.model.quiz import Quiz
from app.service.game_runtime_state import GameRuntimeState
from app.service.game_state_service import GameStateService
from app.ui.console_ui import ConsoleUI


class GamePersistenceService:
    def __init__(
        self,
        state_service: GameStateService,
        console_interface: ConsoleUI,
    ) -> None:
        self.state_service = state_service
        self.console_interface = console_interface

    def save_runtime_state(self, runtime_state: GameRuntimeState) -> None:
        try:
            runtime_state.save_with(self.state_service)
        except OSError:
            self.console_interface.show_error(c.ERROR_STATE_SAVE)
            return

    def save_state_values(
        self,
        quizzes: list[Quiz],
        best_score: Optional[int],
        history: list[dict[str, Any]],
    ) -> None:
        try:
            self.state_service.save_state(quizzes, best_score, history)
        except OSError:
            self.console_interface.show_error(c.ERROR_STATE_SAVE)
