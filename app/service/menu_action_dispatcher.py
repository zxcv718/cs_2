import app.config.constants as constants
from app.service.game_runtime_state import GameRuntimeState
from app.service.game_shutdown_service import GameShutdownService
from app.service.menu_execution import MenuExecution
from app.service.quiz_metrics import MenuChoice
from app.ui.console_ui import ConsoleUI


class MenuActionDispatcher:
    def __init__(
        self,
        menu_execution: MenuExecution,
        game_shutdown_service: GameShutdownService,
    ) -> None:
        self.menu_execution = menu_execution
        self.game_shutdown_service = game_shutdown_service

    def dispatch(
        self,
        menu_choice: MenuChoice,
        runtime_state: GameRuntimeState,
        has_delete: bool,
        console_interface: ConsoleUI,
    ) -> bool:
        menu_execution = self.menu_execution
        game_shutdown_service = self.game_shutdown_service
        if menu_choice.matches(constants.MENU_PLAY):
            menu_execution.play(console_interface, runtime_state)
            return True

        if menu_choice.matches(constants.MENU_ADD):
            menu_execution.add(runtime_state)
            return True

        if menu_choice.matches(constants.MENU_LIST):
            menu_execution.show_list(runtime_state)
            return True

        if has_delete and menu_choice.matches(constants.MENU_DELETE):
            menu_execution.delete(runtime_state)
            return True

        if menu_choice.matches_score(has_delete):
            menu_execution.show_best_score(console_interface, runtime_state)
            return True

        game_shutdown_service.handle_normal_exit(runtime_state)
        return False

    def persist(self, runtime_state: GameRuntimeState) -> None:
        menu_execution = self.menu_execution
        menu_execution.persist(runtime_state)

    def handle_interrupted_session(
        self,
        runtime_state: GameRuntimeState,
        result,
    ) -> None:
        game_shutdown_service = self.game_shutdown_service
        game_shutdown_service.handle_interrupted_session(runtime_state, result)

    def handle_interrupted_program(self, runtime_state: GameRuntimeState) -> None:
        game_shutdown_service = self.game_shutdown_service
        game_shutdown_service.handle_interrupted_program(runtime_state)
