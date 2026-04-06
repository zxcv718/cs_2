import app.config.constants as c
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
        recorded_result = self.result_recorder.record(runtime_state, result)
        self.persistence_service.save_runtime_state(runtime_state)
        console_interface.show_result(
            result.correct_count,
            recorded_result.score,
            result.total_questions,
            result.hint_used_count,
        )
        if recorded_result.is_new_record:
            console_interface.show_message(c.MESSAGE_BEST_SCORE_UPDATED)
