import app.config.constants as c
from app.service.game_persistence_service import GamePersistenceService
from app.service.game_runtime_state import GameRuntimeState
from app.service.game_shutdown_service import GameShutdownService
from app.service.quiz_catalog_service import QuizCatalogService
from app.service.quiz_result_recorder import QuizResultRecorder
from app.service.quiz_session_service import QuizSessionService
from app.ui.console_ui import ConsoleUI


class MenuActionDispatcher:
    def __init__(self, ui: ConsoleUI) -> None:
        self.ui = ui

    def dispatch(
        self,
        choice: int,
        runtime_state: GameRuntimeState,
        has_delete: bool,
        catalog_service: QuizCatalogService,
        session_service: QuizSessionService,
        persistence_service: GamePersistenceService,
        result_recorder: QuizResultRecorder,
        shutdown_service: GameShutdownService,
    ) -> bool:
        if choice == c.MENU_PLAY:
            self.play_quiz(
                runtime_state,
                session_service,
                persistence_service,
                result_recorder,
            )
            return True

        if choice == c.MENU_ADD:
            self.add_quiz(runtime_state, catalog_service, persistence_service)
            return True

        if choice == c.MENU_LIST:
            catalog_service.list_quizzes(runtime_state.quizzes)
            return True

        if has_delete and choice == c.MENU_DELETE:
            self.delete_quiz(runtime_state, catalog_service, persistence_service)
            return True

        if self._is_score_choice(choice, has_delete):
            self.ui.show_best_score(runtime_state.best_score)
            return True

        shutdown_service.handle_normal_exit(runtime_state)
        return False

    def play_quiz(
        self,
        runtime_state: GameRuntimeState,
        session_service: QuizSessionService,
        persistence_service: GamePersistenceService,
        result_recorder: QuizResultRecorder,
    ) -> None:
        result = session_service.play(runtime_state.quizzes)
        if result is None:
            return

        recorded_result = result_recorder.record(runtime_state, result)
        persistence_service.save_runtime_state(runtime_state)
        self.ui.show_result(
            result.correct_count,
            recorded_result.score,
            result.total_questions,
            result.hint_used_count,
        )
        if recorded_result.is_new_record:
            self.ui.show_message(c.MESSAGE_BEST_SCORE_UPDATED)

    def add_quiz(
        self,
        runtime_state: GameRuntimeState,
        catalog_service: QuizCatalogService,
        persistence_service: GamePersistenceService,
    ) -> None:
        if catalog_service.add_quiz(runtime_state.quizzes):
            persistence_service.save_runtime_state(runtime_state)

    def delete_quiz(
        self,
        runtime_state: GameRuntimeState,
        catalog_service: QuizCatalogService,
        persistence_service: GamePersistenceService,
    ) -> None:
        if catalog_service.delete_quiz(runtime_state.quizzes):
            persistence_service.save_runtime_state(runtime_state)

    def _is_score_choice(self, choice: int, has_delete: bool) -> bool:
        if has_delete:
            return choice == c.MENU_SCORE
        return choice == c.MENU_DELETE
