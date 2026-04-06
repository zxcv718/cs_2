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
        if not self.quiz_catalog_service.add_quiz(runtime_state.quiz_catalog):
            return
        self.persistence_service.save_runtime_state(runtime_state)

    def delete(self, runtime_state: GameRuntimeState) -> None:
        if not self.quiz_catalog_service.delete_quiz(runtime_state.quiz_catalog):
            return
        self.persistence_service.save_runtime_state(runtime_state)

    def show_list(self, runtime_state: GameRuntimeState) -> None:
        self.quiz_catalog_service.list_quizzes(runtime_state.quiz_catalog)

    def persist(self, runtime_state: GameRuntimeState) -> None:
        self.persistence_service.save_runtime_state(runtime_state)
