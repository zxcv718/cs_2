from app.application.menu_execution import MenuActions
from app.application.play.quiz_session_models import QuizPerformance
from app.application.state.game_runtime_state import GameRuntimeState
from app.application.state.game_shutdown_service import GameShutdownService
from app.console.interface import ConsoleInterface
from app.service.quiz_metrics import DeleteMenuAvailability, MenuChoice


class MenuActionDispatcher:
    def __init__(
        self,
        menu_actions: MenuActions,
        game_shutdown_service: GameShutdownService,
    ) -> None:
        self.menu_actions = menu_actions
        self.game_shutdown_service = game_shutdown_service

    def dispatch(
        self,
        menu_choice: MenuChoice,
        runtime_state: GameRuntimeState,
        delete_menu_availability: DeleteMenuAvailability,
        console_interface: ConsoleInterface,
    ) -> bool:
        menu_actions = self.menu_actions
        if menu_actions.execute_matching(
            menu_choice,
            delete_menu_availability,
            console_interface,
            runtime_state,
        ):
            return True

        game_shutdown_service = self.game_shutdown_service
        game_shutdown_service.handle_normal_exit(runtime_state)
        return False

    def persist(self, runtime_state: GameRuntimeState) -> None:
        menu_actions = self.menu_actions
        menu_actions.persist(runtime_state)

    def handle_interrupted_session(
        self,
        runtime_state: GameRuntimeState,
        result: QuizPerformance | None,
    ) -> None:
        game_shutdown_service = self.game_shutdown_service
        game_shutdown_service.handle_interrupted_session(runtime_state, result)

    def handle_interrupted_program(self, runtime_state: GameRuntimeState) -> None:
        game_shutdown_service = self.game_shutdown_service
        game_shutdown_service.handle_interrupted_program(runtime_state)
