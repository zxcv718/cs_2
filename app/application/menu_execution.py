from app.application.catalog.quiz_catalog_listing_service import QuizCatalogListingService
from app.application.catalog.quiz_catalog_mutation_workflow import QuizCatalogMutationWorkflow
from app.application.play.quiz_play_workflow import QuizPlayWorkflow
from app.application.state.game_persistence_service import GamePersistenceService
from app.application.state.game_runtime_state import GameRuntimeState
from app.console.interface import ConsoleInterface
from app.presentation.best_score_display_service import BestScoreDisplayService


class MenuExecution:
    def __init__(
        self,
        quiz_play_workflow: QuizPlayWorkflow,
        quiz_catalog_mutation_workflow: QuizCatalogMutationWorkflow,
        quiz_catalog_listing_service: QuizCatalogListingService,
        best_score_display_service: BestScoreDisplayService,
        persistence_service: GamePersistenceService,
    ) -> None:
        self.quiz_play_workflow = quiz_play_workflow
        self.quiz_catalog_mutation_workflow = quiz_catalog_mutation_workflow
        self.quiz_catalog_listing_service = quiz_catalog_listing_service
        self.best_score_display_service = best_score_display_service
        self.persistence_service = persistence_service

    def play(
        self,
        console_interface: ConsoleInterface,
        runtime_state: GameRuntimeState,
    ) -> None:
        quiz_play_workflow = self.quiz_play_workflow
        quiz_play_workflow.play(console_interface, runtime_state)

    def add(self, runtime_state: GameRuntimeState) -> None:
        quiz_catalog_mutation_workflow = self.quiz_catalog_mutation_workflow
        quiz_catalog_mutation_workflow.add(runtime_state)

    def delete(self, runtime_state: GameRuntimeState) -> None:
        quiz_catalog_mutation_workflow = self.quiz_catalog_mutation_workflow
        quiz_catalog_mutation_workflow.delete(runtime_state)

    def show_list(self, runtime_state: GameRuntimeState) -> None:
        quiz_catalog_listing_service = self.quiz_catalog_listing_service
        quiz_catalog = runtime_state.quiz_catalog
        quiz_catalog_listing_service.show_quizzes(quiz_catalog)

    def show_best_score(
        self,
        console_interface: ConsoleInterface,
        runtime_state: GameRuntimeState,
    ) -> None:
        best_score_display_service = self.best_score_display_service
        best_score_display_service.show(console_interface, runtime_state)

    def persist(self, runtime_state: GameRuntimeState) -> None:
        persistence_service = self.persistence_service
        persistence_service.save_runtime_state(runtime_state)
