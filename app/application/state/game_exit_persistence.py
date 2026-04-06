from typing import Optional

from app.application.play.best_score_service import RecordUpdateStatus
from app.application.play.quiz_result_recorder import QuizResultRecorder
from app.application.play.quiz_session_models import QuizPerformance
from app.application.state.game_persistence_service import GamePersistenceService
from app.application.state.game_runtime_state import GameRuntimeState


class GameExitPersistence:
    def __init__(
        self,
        persistence_service: GamePersistenceService,
        result_recorder: QuizResultRecorder,
    ) -> None:
        self.persistence_service = persistence_service
        self.result_recorder = result_recorder

    def persist_normal_exit(self, runtime_state: GameRuntimeState) -> None:
        persistence_service = self.persistence_service
        persistence_service.save_runtime_state(runtime_state)

    def persist_interrupted_program(self, runtime_state: GameRuntimeState) -> None:
        persistence_service = self.persistence_service
        persistence_service.save_runtime_state(runtime_state)

    def persist_interrupted_session(
        self,
        runtime_state: GameRuntimeState,
        result: QuizPerformance | None,
    ) -> RecordUpdateStatus:
        if result is not None:
            result_recorder = self.result_recorder
            persistence_service = self.persistence_service
            score_outcome = result_recorder.record(runtime_state, result)
            persistence_service.save_runtime_state(runtime_state)
            return score_outcome.record_update_status()

        persistence_service = self.persistence_service
        persistence_service.save_runtime_state(runtime_state)
        return RecordUpdateStatus.unchanged()
