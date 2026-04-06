from app.application.play.quiz_play_result_handler import QuizPlayResultHandler
from app.application.play.quiz_session_service import QuizSessionService
from app.application.state.game_runtime_state import GameRuntimeState
from app.console.interface import ConsoleInterface


class QuizPlayWorkflow:
    def __init__(
        self,
        quiz_session_service: QuizSessionService,
        quiz_play_result_handler: QuizPlayResultHandler,
    ) -> None:
        self.quiz_session_service = quiz_session_service
        self.quiz_play_result_handler = quiz_play_result_handler

    def play(
        self,
        console_interface: ConsoleInterface,
        runtime_state: GameRuntimeState,
    ) -> None:
        quiz_session_service = self.quiz_session_service
        quiz_catalog = runtime_state.quiz_catalog
        result = quiz_session_service.play(quiz_catalog)
        if result is None:
            return
        quiz_play_result_handler = self.quiz_play_result_handler
        quiz_play_result_handler.handle(
            console_interface,
            runtime_state,
            result,
        )
