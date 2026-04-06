from typing import Optional

from app.service.game_persistence_service import GamePersistenceService
from app.service.game_runtime_state import GameRuntimeState
from app.service.quiz_result_recorder import QuizResultRecorder
from app.service.quiz_session_models import QuizSessionResult


class GameExitPersistence:
    def __init__(
        self,
        persistence_service: GamePersistenceService,
        result_recorder: QuizResultRecorder,
    ) -> None:
        self.persistence_service = persistence_service
        self.result_recorder = result_recorder

    def persist_normal_exit(self, runtime_state: GameRuntimeState) -> None:
        self.persistence_service.save_runtime_state(runtime_state)

    def persist_interrupted_program(self, runtime_state: GameRuntimeState) -> None:
        self.persistence_service.save_runtime_state(runtime_state)

    def persist_interrupted_session(
        self,
        runtime_state: GameRuntimeState,
        result: Optional[QuizSessionResult],
    ) -> bool:
        if result is not None:
            recorded_result = self.result_recorder.record(runtime_state, result)
            self.persistence_service.save_runtime_state(runtime_state)
            return recorded_result.is_new_record

        self.persistence_service.save_runtime_state(runtime_state)
        return False
