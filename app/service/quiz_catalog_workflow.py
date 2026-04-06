from app.service.game_persistence_service import GamePersistenceService
from app.service.game_runtime_state import GameRuntimeState
from app.service.quiz_catalog_service import QuizCatalogService


class QuizCatalogWorkflow:
    def __init__(
        self,
        quiz_catalog_service: QuizCatalogService,
        persistence_service: GamePersistenceService,
    ) -> None:
        self.quiz_catalog_service = quiz_catalog_service
        self.persistence_service = persistence_service

    def add(self, runtime_state: GameRuntimeState) -> None:
        quiz_catalog_service = self.quiz_catalog_service
        quiz_catalog = runtime_state.quiz_catalog
        if not quiz_catalog_service.add_quiz(quiz_catalog):
            return
        persistence_service = self.persistence_service
        persistence_service.save_runtime_state(runtime_state)

    def delete(self, runtime_state: GameRuntimeState) -> None:
        quiz_catalog_service = self.quiz_catalog_service
        quiz_catalog = runtime_state.quiz_catalog
        if not quiz_catalog_service.delete_quiz(quiz_catalog):
            return
        persistence_service = self.persistence_service
        persistence_service.save_runtime_state(runtime_state)

    def show_list(self, runtime_state: GameRuntimeState) -> None:
        quiz_catalog_service = self.quiz_catalog_service
        quiz_catalog = runtime_state.quiz_catalog
        quiz_catalog_service.list_quizzes(quiz_catalog)

    def persist(self, runtime_state: GameRuntimeState) -> None:
        persistence_service = self.persistence_service
        persistence_service.save_runtime_state(runtime_state)
