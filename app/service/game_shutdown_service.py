from typing import Optional

import app.config.constants as constants
from app.service.game_exit_persistence import GameExitPersistence
from app.service.game_runtime_state import GameRuntimeState
from app.service.quiz_session_models import QuizSessionResult
from app.console_interface import ConsoleInterface


class GameShutdownService:
    def __init__(
        self,
        console_interface: ConsoleInterface,
        game_exit_persistence: GameExitPersistence,
    ) -> None:
        self.console_interface = console_interface
        self.game_exit_persistence = game_exit_persistence

    def handle_normal_exit(self, runtime_state: GameRuntimeState) -> None:
        game_exit_persistence = self.game_exit_persistence
        console_interface = self.console_interface
        game_exit_persistence.persist_normal_exit(runtime_state)
        console_interface.show_message(constants.MESSAGE_PROGRAM_EXIT)

    def handle_interrupted_session(
        self,
        runtime_state: GameRuntimeState,
        result: Optional[QuizSessionResult],
    ) -> None:
        game_exit_persistence = self.game_exit_persistence
        console_interface = self.console_interface
        if game_exit_persistence.persist_interrupted_session(runtime_state, result):
            console_interface.show_message(constants.MESSAGE_BEST_SCORE_UPDATED)

        console_interface.show_message(constants.MESSAGE_INTERRUPTED_EXIT)

    def handle_interrupted_program(self, runtime_state: GameRuntimeState) -> None:
        console_interface = self.console_interface
        game_exit_persistence = self.game_exit_persistence
        console_interface.show_message(constants.MESSAGE_INTERRUPTED_EXIT)
        game_exit_persistence.persist_interrupted_program(runtime_state)
