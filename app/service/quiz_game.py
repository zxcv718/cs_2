import app.config.constants as c
from app.repository.state_repository import StateRepository
from app.service.best_score_service import BestScoreService
from app.service.default_game_state_factory import DefaultGameStateFactory
from app.service.default_state_recovery import DefaultStateRecovery
from app.service.game_bootstrap_service import GameBootstrapService
from app.service.game_exit_persistence import GameExitPersistence
from app.service.game_persistence_service import GamePersistenceService
from app.service.game_runtime_state import GameRuntimeState
from app.service.game_shutdown_service import GameShutdownService
from app.service.game_state_service import GameStateService
from app.service.menu_action_dispatcher import MenuActionDispatcher
from app.service.menu_execution import MenuExecution
from app.service.quiz_history_service import QuizHistoryService
from app.service.quiz_catalog_service import QuizCatalogService
from app.service.quiz_catalog_workflow import QuizCatalogWorkflow
from app.service.quiz_game_execution import QuizGameExecution
from app.service.quiz_game_runner import QuizGameRunner
from app.service.quiz_play_result_handler import QuizPlayResultHandler
from app.service.quiz_play_workflow import QuizPlayWorkflow
from app.service.quiz_result_recorder import QuizResultRecorder
from app.service.quiz_score_keeper import QuizScoreKeeper
from app.service.quiz_session_service import QuizSessionService
from app.service.quiz_scoring_service import QuizScoringService
from app.ui.console_ui import ConsoleUI


# 전체 프로그램 흐름을 조율하는 메인 서비스입니다.
class QuizGame:
    def __init__(
        self,
        console_interface: ConsoleUI,
        state_repository: StateRepository,
    ) -> None:
        state_service = GameStateService(state_repository)
        persistence_service = GamePersistenceService(state_service, console_interface)
        score_keeper = QuizScoreKeeper(
            QuizScoringService(),
            BestScoreService(),
        )
        result_recorder = QuizResultRecorder(
            score_keeper,
            QuizHistoryService(),
        )
        default_state_recovery = DefaultStateRecovery(
            DefaultGameStateFactory(),
            persistence_service,
        )
        game_exit_persistence = GameExitPersistence(
            persistence_service,
            result_recorder,
        )
        quiz_play_result_handler = QuizPlayResultHandler(
            persistence_service,
            result_recorder,
        )
        quiz_play_workflow = QuizPlayWorkflow(
            QuizSessionService(console_interface),
            quiz_play_result_handler,
        )
        quiz_catalog_workflow = QuizCatalogWorkflow(
            QuizCatalogService(console_interface),
            persistence_service,
        )
        menu_execution = MenuExecution(
            quiz_play_workflow,
            quiz_catalog_workflow,
        )

        self.runtime_state = GameRuntimeState()
        bootstrap_service = GameBootstrapService(
            state_service,
            default_state_recovery,
        )
        shutdown_service = GameShutdownService(
            console_interface,
            game_exit_persistence,
        )
        menu_action_dispatcher = MenuActionDispatcher(
            menu_execution,
            shutdown_service,
        )
        quiz_game_execution = QuizGameExecution(
            bootstrap_service,
            menu_action_dispatcher,
        )
        self.quiz_game_runner = QuizGameRunner(
            console_interface,
            quiz_game_execution,
        )

    def initialize_state(self) -> None:
        self.quiz_game_runner.initialize_state(self.runtime_state)

    def persist_state(self) -> None:
        self.quiz_game_runner.persist_state(self.runtime_state)

    def run(self) -> None:
        self.quiz_game_runner.run(self.runtime_state)
