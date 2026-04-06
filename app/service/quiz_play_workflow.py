from app.service.game_runtime_state import GameRuntimeState
from app.service.quiz_play_result_handler import QuizPlayResultHandler
from app.service.quiz_session_service import QuizSessionService
from app.ui.console_ui import ConsoleUI


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
        console_interface: ConsoleUI,
        runtime_state: GameRuntimeState,
    ) -> None:
        result = self.quiz_session_service.play(runtime_state.quiz_catalog)
        if result is None:
            return
        self.quiz_play_result_handler.handle(
            console_interface,
            runtime_state,
            result,
        )
