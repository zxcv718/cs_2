from app.application.catalog.quiz_catalog_creation_service import QuizCatalogCreationService
from app.application.catalog.quiz_catalog_deletion_service import QuizCatalogDeletionService
from app.application.state.game_persistence_service import GamePersistenceService
from app.application.state.game_runtime_state import GameRuntimeState


class QuizCatalogMutationWorkflow:
    def __init__(
        self,
        creation_service: QuizCatalogCreationService,
        deletion_service: QuizCatalogDeletionService,
        persistence_service: GamePersistenceService,
    ) -> None:
        self.creation_service = creation_service
        self.deletion_service = deletion_service
        self.persistence_service = persistence_service

    def add(self, runtime_state: GameRuntimeState) -> None:
        creation_service = self.creation_service
        quiz_catalog = runtime_state.quiz_catalog
        if not creation_service.add_quiz(quiz_catalog):
            return
        persistence_service = self.persistence_service
        persistence_service.save_runtime_state(runtime_state)

    def delete(self, runtime_state: GameRuntimeState) -> None:
        deletion_service = self.deletion_service
        quiz_catalog = runtime_state.quiz_catalog
        if not deletion_service.delete_quiz(quiz_catalog):
            return
        persistence_service = self.persistence_service
        persistence_service.save_runtime_state(runtime_state)
