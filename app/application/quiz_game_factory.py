from app.application.catalog.quiz_catalog_creation_service import QuizCatalogCreationService
from app.application.catalog.quiz_catalog_deletion_service import QuizCatalogDeletionService
from app.application.catalog.quiz_catalog_listing_service import QuizCatalogListingService
from app.application.menu_action_dispatcher import MenuActionDispatcher
from app.application.menu_execution import (
    AddMenuAction,
    BestScoreMenuAction,
    DeleteMenuAction,
    ListMenuAction,
    MenuActionCollection,
    MenuActions,
    PlayMenuAction,
)
from app.application.play.best_score_service import BestScoreService
from app.application.play.question_count_chooser import QuestionCountChooser
from app.application.play.quiz_history_service import QuizHistoryService
from app.application.play.quiz_play_result_handler import QuizPlayResultHandler
from app.application.play.quiz_play_workflow import QuizPlayWorkflow
from app.application.play.quiz_result_recorder import QuizResultRecorder
from app.application.play.quiz_score_keeper import QuizScoreKeeper
from app.application.play.quiz_scoring_service import QuizScoringService
from app.application.play.quiz_session_service import QuizSessionService
from app.application.quiz_game import QuizGame
from app.application.quiz_game_execution import QuizGameExecution
from app.application.quiz_game_runner import QuizGameRunner
from app.application.state.default_game_state_factory import DefaultGameStateFactory
from app.application.state.default_state_recovery import (
    DefaultStateRecovery,
    StateRecoveryPersistence,
    StateRecoveryPolicy,
)
from app.application.state.game_bootstrap_service import GameBootstrapService
from app.application.state.game_exit_persistence import GameExitPersistence
from app.application.state.game_persistence_service import GamePersistenceService
from app.application.state.game_runtime_state import GameRuntimeState
from app.application.state.game_shutdown_service import GameShutdownService
from app.application.state.game_state_service import GameStateService
from app.console.interface import ConsoleInterface
from app.presentation.best_score_display_service import BestScoreDisplayService
from app.repository.state_repository import StateRepository


class QuizGameFactory:
    def create(
        self,
        console_interface: ConsoleInterface,
        state_repository: StateRepository,
    ) -> QuizGame:
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
        recovery_policy = StateRecoveryPolicy(
            DefaultGameStateFactory(),
            state_service,
        )
        default_state_recovery = DefaultStateRecovery(
            recovery_policy,
            StateRecoveryPersistence(persistence_service),
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
            QuizSessionService(
                console_interface,
                QuestionCountChooser(console_interface),
            ),
            quiz_play_result_handler,
        )
        menu_actions = MenuActions(
            MenuActionCollection(
                (
                    PlayMenuAction(quiz_play_workflow),
                    AddMenuAction(
                        QuizCatalogCreationService(console_interface),
                        persistence_service,
                    ),
                    ListMenuAction(QuizCatalogListingService(console_interface)),
                    DeleteMenuAction(
                        QuizCatalogDeletionService(console_interface),
                        persistence_service,
                    ),
                    BestScoreMenuAction(BestScoreDisplayService()),
                )
            ),
            persistence_service,
        )

        runtime_state = GameRuntimeState()
        bootstrap_service = GameBootstrapService(
            state_service,
            default_state_recovery,
        )
        shutdown_service = GameShutdownService(
            console_interface,
            game_exit_persistence,
        )
        menu_action_dispatcher = MenuActionDispatcher(
            menu_actions,
            shutdown_service,
        )
        quiz_game_execution = QuizGameExecution(
            bootstrap_service,
            menu_action_dispatcher,
        )
        quiz_game_runner = QuizGameRunner(
            console_interface,
            quiz_game_execution,
        )
        return QuizGame(runtime_state, quiz_game_runner)
