import app.config.constants as c
from app.model.quiz import Quiz
from app.repository.state_repository import StateRepository
from app.service.best_score_service import BestScoreService
from app.service.default_game_state_factory import DefaultGameStateFactory
from app.service.game_bootstrap_service import GameBootstrapService
from app.service.game_persistence_service import GamePersistenceService
from app.service.game_runtime_state import GameRuntimeState
from app.service.game_shutdown_service import GameShutdownService
from app.service.game_state_service import GameStateService
from app.service.menu_action_dispatcher import MenuActionDispatcher
from app.service.quiz_history_service import QuizHistoryService
from app.service.quiz_catalog_service import QuizCatalogService
from app.service.quiz_result_recorder import QuizResultRecorder
from app.service.quiz_session_service import (
    QuizSessionInterrupted,
    QuizSessionService,
)
from app.service.quiz_scoring_service import QuizScoringService
from app.ui.console_ui import ConsoleUI
from typing import Any, Optional


# 전체 프로그램 흐름을 조율하는 메인 서비스입니다.
class QuizGame:
    def __init__(self, ui: ConsoleUI, state_repository: StateRepository) -> None:
        self.ui = ui
        self.state_repository = state_repository
        state_service = GameStateService(state_repository)
        persistence_service = GamePersistenceService(state_service, ui)
        result_recorder = QuizResultRecorder(
            QuizScoringService(),
            BestScoreService(),
            QuizHistoryService(),
        )

        self.runtime_state = GameRuntimeState()
        self.state_service = state_service
        self.persistence_service = persistence_service
        self.default_state_factory = DefaultGameStateFactory()
        self.bootstrap_service = GameBootstrapService(
            ui,
            state_service,
            self.default_state_factory,
            persistence_service,
        )
        self.catalog_service = QuizCatalogService(ui)
        self.session_service = QuizSessionService(ui)
        self.result_recorder = result_recorder
        self.shutdown_service = GameShutdownService(
            ui,
            persistence_service,
            result_recorder,
        )
        self.menu_dispatcher = MenuActionDispatcher(ui)

    def initialize_state(self) -> None:
        self.bootstrap_service.initialize(self.runtime_state)

    def persist_state(self) -> None:
        self.persistence_service.save_runtime_state(self.runtime_state)

    def run(self) -> None:
        if not self.runtime_state.initialized:
            self.initialize_state()

        has_delete = c.ENABLE_DELETE_MENU
        max_choice = (
            c.MENU_MAX_CHOICE_WITH_DELETE
            if has_delete
            else c.MENU_MAX_CHOICE_WITHOUT_DELETE
        )

        while True:
            try:
                self.ui.show_menu(has_delete=has_delete)
                choice = self.ui.get_menu_choice(c.MENU_MIN_CHOICE, max_choice)

                if not self.menu_dispatcher.dispatch(
                    choice,
                    self.runtime_state,
                    has_delete,
                    self.catalog_service,
                    self.session_service,
                    self.persistence_service,
                    self.result_recorder,
                    self.shutdown_service,
                ):
                    break
            except QuizSessionInterrupted as interrupted:
                self.shutdown_service.handle_interrupted_session(
                    self.runtime_state,
                    interrupted.partial_result,
                )
                break
            except (KeyboardInterrupt, EOFError):
                self.shutdown_service.handle_interrupted_program(self.runtime_state)
                break

    def play_quiz(self) -> None:
        self.menu_dispatcher.play_quiz(
            self.runtime_state,
            self.session_service,
            self.persistence_service,
            self.result_recorder,
        )

    def add_quiz(self) -> None:
        self.menu_dispatcher.add_quiz(
            self.runtime_state,
            self.catalog_service,
            self.persistence_service,
        )

    def list_quizzes(self) -> None:
        self.catalog_service.list_quizzes(self.runtime_state.quizzes)

    def show_best_score(self) -> None:
        self.ui.show_best_score(self.runtime_state.best_score)

    def delete_quiz(self) -> None:
        self.menu_dispatcher.delete_quiz(
            self.runtime_state,
            self.catalog_service,
            self.persistence_service,
        )

    @property
    def quizzes(self) -> list[Quiz]:
        return self.runtime_state.quizzes

    @quizzes.setter
    def quizzes(self, quizzes: list[Quiz]) -> None:
        self.runtime_state.quizzes = quizzes

    @property
    def best_score(self) -> Optional[int]:
        return self.runtime_state.best_score

    @best_score.setter
    def best_score(self, best_score: Optional[int]) -> None:
        self.runtime_state.best_score = best_score

    @property
    def history(self) -> list[dict[str, Any]]:
        return self.runtime_state.history

    @history.setter
    def history(self, history: list[dict[str, Any]]) -> None:
        self.runtime_state.history = history
