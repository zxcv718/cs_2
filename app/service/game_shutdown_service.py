from typing import Optional

import app.config.constants as c
from app.service.game_persistence_service import GamePersistenceService
from app.service.game_runtime_state import GameRuntimeState
from app.service.quiz_result_recorder import QuizResultRecorder
from app.service.quiz_session_service import QuizSessionResult
from app.ui.console_ui import ConsoleUI


class GameShutdownService:
    def __init__(
        self,
        ui: ConsoleUI,
        persistence_service: GamePersistenceService,
        result_recorder: QuizResultRecorder,
    ) -> None:
        self.ui = ui
        self.persistence_service = persistence_service
        self.result_recorder = result_recorder

    def handle_normal_exit(self, runtime_state: GameRuntimeState) -> None:
        self.persistence_service.save_runtime_state(runtime_state)
        self.ui.show_message(c.MESSAGE_PROGRAM_EXIT)

    def handle_interrupted_session(
        self,
        runtime_state: GameRuntimeState,
        result: Optional[QuizSessionResult],
    ) -> None:
        if result is not None:
            recorded_result = self.result_recorder.record(runtime_state, result)
            if recorded_result.is_new_record:
                self.ui.show_message(c.MESSAGE_BEST_SCORE_UPDATED)

        self.ui.show_message(c.MESSAGE_INTERRUPTED_EXIT)
        self.persistence_service.save_runtime_state(runtime_state)

    def handle_interrupted_program(self, runtime_state: GameRuntimeState) -> None:
        self.ui.show_message(c.MESSAGE_INTERRUPTED_EXIT)
        self.persistence_service.save_runtime_state(runtime_state)
