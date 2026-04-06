from typing import Optional

import app.config.constants as c
from app.service.game_exit_persistence import GameExitPersistence
from app.service.game_runtime_state import GameRuntimeState
from app.service.quiz_session_models import QuizSessionResult
from app.ui.console_ui import ConsoleUI


class GameShutdownService:
    def __init__(
        self,
        console_interface: ConsoleUI,
        game_exit_persistence: GameExitPersistence,
    ) -> None:
        self.console_interface = console_interface
        self.game_exit_persistence = game_exit_persistence

    def handle_normal_exit(self, runtime_state: GameRuntimeState) -> None:
        self.game_exit_persistence.persist_normal_exit(runtime_state)
        self.console_interface.show_message(c.MESSAGE_PROGRAM_EXIT)

    def handle_interrupted_session(
        self,
        runtime_state: GameRuntimeState,
        result: Optional[QuizSessionResult],
    ) -> None:
        if self.game_exit_persistence.persist_interrupted_session(runtime_state, result):
            self.console_interface.show_message(c.MESSAGE_BEST_SCORE_UPDATED)

        self.console_interface.show_message(c.MESSAGE_INTERRUPTED_EXIT)

    def handle_interrupted_program(self, runtime_state: GameRuntimeState) -> None:
        self.console_interface.show_message(c.MESSAGE_INTERRUPTED_EXIT)
        self.game_exit_persistence.persist_interrupted_program(runtime_state)
