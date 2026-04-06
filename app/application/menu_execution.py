from dataclasses import dataclass, field
from typing import Iterator, Protocol

import app.config.constants as constants
from app.application.catalog.quiz_catalog_creation_service import QuizCatalogCreationService
from app.application.catalog.quiz_catalog_deletion_service import QuizCatalogDeletionService
from app.application.catalog.quiz_catalog_listing_service import QuizCatalogListingService
from app.application.play.quiz_play_workflow import QuizPlayWorkflow
from app.application.state.game_persistence_service import GamePersistenceService
from app.application.state.game_runtime_state import GameRuntimeState
from app.console.interface import ConsoleInterface
from app.presentation.best_score_display_service import BestScoreDisplayService
from app.service.quiz_metrics import DeleteMenuAvailability, MenuChoice


class MenuAction(Protocol):
    def matches(
        self,
        menu_choice: MenuChoice,
        delete_menu_availability: DeleteMenuAvailability,
    ) -> bool:
        ...

    def execute(
        self,
        console_interface: ConsoleInterface,
        runtime_state: GameRuntimeState,
    ) -> None:
        ...


@dataclass(frozen=True)
class PlayMenuAction:
    quiz_play_workflow: QuizPlayWorkflow

    def matches(
        self,
        menu_choice: MenuChoice,
        delete_menu_availability: DeleteMenuAvailability,
    ) -> bool:
        return menu_choice.matches(constants.MENU_PLAY)

    def execute(
        self,
        console_interface: ConsoleInterface,
        runtime_state: GameRuntimeState,
    ) -> None:
        self.quiz_play_workflow.play(console_interface, runtime_state)


@dataclass(frozen=True)
class AddMenuAction:
    quiz_catalog_creation_service: QuizCatalogCreationService
    persistence_service: GamePersistenceService

    def matches(
        self,
        menu_choice: MenuChoice,
        delete_menu_availability: DeleteMenuAvailability,
    ) -> bool:
        return menu_choice.matches(constants.MENU_ADD)

    def execute(
        self,
        console_interface: ConsoleInterface,
        runtime_state: GameRuntimeState,
    ) -> None:
        quiz_catalog = runtime_state.quiz_catalog
        self.quiz_catalog_creation_service.add_quiz(quiz_catalog)
        self.persistence_service.save_runtime_state(runtime_state)


@dataclass(frozen=True)
class ListMenuAction:
    quiz_catalog_listing_service: QuizCatalogListingService

    def matches(
        self,
        menu_choice: MenuChoice,
        delete_menu_availability: DeleteMenuAvailability,
    ) -> bool:
        return menu_choice.matches(constants.MENU_LIST)

    def execute(
        self,
        console_interface: ConsoleInterface,
        runtime_state: GameRuntimeState,
    ) -> None:
        quiz_catalog = runtime_state.quiz_catalog
        self.quiz_catalog_listing_service.show_quizzes(quiz_catalog)


@dataclass(frozen=True)
class DeleteMenuAction:
    quiz_catalog_deletion_service: QuizCatalogDeletionService
    persistence_service: GamePersistenceService

    def matches(
        self,
        menu_choice: MenuChoice,
        delete_menu_availability: DeleteMenuAvailability,
    ) -> bool:
        return menu_choice.matches_delete(delete_menu_availability)

    def execute(
        self,
        console_interface: ConsoleInterface,
        runtime_state: GameRuntimeState,
    ) -> None:
        quiz_catalog = runtime_state.quiz_catalog
        removed_quiz = self.quiz_catalog_deletion_service.delete_quiz(quiz_catalog)
        if removed_quiz is None:
            return
        self.persistence_service.save_runtime_state(runtime_state)


@dataclass(frozen=True)
class BestScoreMenuAction:
    best_score_display_service: BestScoreDisplayService

    def matches(
        self,
        menu_choice: MenuChoice,
        delete_menu_availability: DeleteMenuAvailability,
    ) -> bool:
        return menu_choice.matches_score(delete_menu_availability)

    def execute(
        self,
        console_interface: ConsoleInterface,
        runtime_state: GameRuntimeState,
    ) -> None:
        self.best_score_display_service.show(console_interface, runtime_state)


@dataclass(frozen=True)
class MenuActionCollection:
    actions: tuple[MenuAction, ...] = field(default_factory=tuple)

    def __iter__(self) -> Iterator[MenuAction]:
        return iter(self.actions)


class MenuActions:
    def __init__(
        self,
        menu_action_collection: MenuActionCollection,
        persistence_service: GamePersistenceService,
    ) -> None:
        self.menu_action_collection = menu_action_collection
        self.persistence_service = persistence_service

    def execute_matching(
        self,
        menu_choice: MenuChoice,
        delete_menu_availability: DeleteMenuAvailability,
        console_interface: ConsoleInterface,
        runtime_state: GameRuntimeState,
    ) -> bool:
        action = self._matching_action(menu_choice, delete_menu_availability)
        if action is None:
            return False
        action.execute(console_interface, runtime_state)
        return True

    def _matching_action(
        self,
        menu_choice: MenuChoice,
        delete_menu_availability: DeleteMenuAvailability,
    ) -> MenuAction | None:
        return next(
            (
                action
                for action in self.menu_action_collection
                if action.matches(menu_choice, delete_menu_availability)
            ),
            None,
        )

    def persist(self, runtime_state: GameRuntimeState) -> None:
        self.persistence_service.save_runtime_state(runtime_state)
