import app.config.constants as constants
from app.service.game_persistence_service import GamePersistenceService
from app.service.game_runtime_state import GameRuntimeState
from app.service.quiz_result_recorder import QuizResultRecorder
from app.service.quiz_session_models import QuizSessionResult
from app.ui.console_ui import ConsoleUI


class QuizPlayResultHandler:
    def __init__(
        self,
        persistence_service: GamePersistenceService,
        result_recorder: QuizResultRecorder,
    ) -> None:
        self.persistence_service = persistence_service
        self.result_recorder = result_recorder

    def handle(
        self,
        console_interface: ConsoleUI,
        runtime_state: GameRuntimeState,
        result: QuizSessionResult,
    ) -> None:
        result_recorder = self.result_recorder
        persistence_service = self.persistence_service
        recorded_result = result_recorder.record(runtime_state, result)
        persistence_service.save_runtime_state(runtime_state)
        console_interface.show_result(
            int(result.correct_count),
            int(recorded_result.score),
            int(result.total_questions),
            int(result.hint_used_count),
        )
        if recorded_result.is_new_record:
            console_interface.show_message(constants.MESSAGE_BEST_SCORE_UPDATED)
