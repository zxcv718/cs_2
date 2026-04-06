import app.config.constants as constants
from app.application.play.quiz_result_recorder import QuizResultRecorder
from app.application.play.quiz_session_models import QuizPerformance
from app.application.state.game_persistence_service import GamePersistenceService
from app.application.state.game_runtime_state import GameRuntimeState
from app.console.interface import ConsoleInterface


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
        console_interface: ConsoleInterface,
        runtime_state: GameRuntimeState,
        result: QuizPerformance,
    ) -> None:
        result_recorder = self.result_recorder
        persistence_service = self.persistence_service
        recorded_result = result_recorder.record(runtime_state, result)
        persistence_service.save_runtime_state(runtime_state)
        console_interface.show_result(
            int(result.correct_answers()),
            int(recorded_result.score_value()),
            int(result.question_count()),
            int(result.hint_usages()),
        )
        record_update_status = recorded_result.record_update_status()
        if record_update_status.is_updated():
            console_interface.show_message(constants.MESSAGE_BEST_SCORE_UPDATED)
