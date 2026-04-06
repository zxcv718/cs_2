import app.config.constants as c
from app.service.game_runtime_state import GameRuntimeState
from app.service.game_shutdown_service import GameShutdownService
from app.service.menu_execution import MenuExecution
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
        choice: int,
        runtime_state: GameRuntimeState,
        has_delete: bool,
        console_interface: ConsoleUI,
    ) -> bool:
        if choice == c.MENU_PLAY:
            self.menu_execution.play(console_interface, runtime_state)
            return True

        if choice == c.MENU_ADD:
            self.menu_execution.add(runtime_state)
            return True

        if choice == c.MENU_LIST:
            self.menu_execution.show_list(runtime_state)
            return True

        if has_delete and choice == c.MENU_DELETE:
            self.menu_execution.delete(runtime_state)
            return True

        if self._is_score_choice(choice, has_delete):
            self.menu_execution.show_best_score(console_interface, runtime_state)
            return True

        self.game_shutdown_service.handle_normal_exit(runtime_state)
        return False

    def persist(self, runtime_state: GameRuntimeState) -> None:
        self.menu_execution.persist(runtime_state)

    def handle_interrupted_session(
        self,
        runtime_state: GameRuntimeState,
        result,
    ) -> None:
        self.game_shutdown_service.handle_interrupted_session(runtime_state, result)

    def handle_interrupted_program(self, runtime_state: GameRuntimeState) -> None:
        self.game_shutdown_service.handle_interrupted_program(runtime_state)

    def _is_score_choice(self, choice: int, has_delete: bool) -> bool:
        if has_delete:
            return choice == c.MENU_SCORE
        return choice == c.MENU_DELETE
