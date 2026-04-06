import app.config.constants as c
from app.service.game_bootstrap_service import GameBootstrapService
from app.service.game_runtime_state import GameRuntimeState
from app.service.menu_action_dispatcher import MenuActionDispatcher
from app.service.quiz_session_models import QuizSessionInterrupted
from app.ui.console_ui import ConsoleUI


class QuizGameExecution:
    def __init__(
        self,
        game_bootstrap_service: GameBootstrapService,
        menu_action_dispatcher: MenuActionDispatcher,
    ) -> None:
        self.game_bootstrap_service = game_bootstrap_service
        self.menu_action_dispatcher = menu_action_dispatcher

    def initialize_state(
        self,
        runtime_state: GameRuntimeState,
        console_interface: ConsoleUI,
    ) -> None:
        runtime_state.initialize_with(
            self.game_bootstrap_service,
            console_interface,
        )

    def persist_state(self, runtime_state: GameRuntimeState) -> None:
        self.menu_action_dispatcher.persist(runtime_state)

    def run(
        self,
        runtime_state: GameRuntimeState,
        console_interface: ConsoleUI,
    ) -> None:
        self.initialize_state(runtime_state, console_interface)
        has_delete = c.ENABLE_DELETE_MENU
        maximum_menu_choice = self._maximum_menu_choice(has_delete)
        self._run_loop(
            runtime_state,
            has_delete,
            maximum_menu_choice,
            console_interface,
        )

    def _run_loop(
        self,
        runtime_state: GameRuntimeState,
        has_delete: bool,
        maximum_menu_choice: int,
        console_interface: ConsoleUI,
    ) -> None:
        while True:
            try:
                console_interface.show_menu(has_delete=has_delete)
                choice = console_interface.get_menu_choice(
                    c.MENU_MIN_CHOICE,
                    maximum_menu_choice,
                )
                if not self.menu_action_dispatcher.dispatch(
                    choice,
                    runtime_state,
                    has_delete,
                    console_interface,
                ):
                    return
            except QuizSessionInterrupted as interrupted:
                self.menu_action_dispatcher.handle_interrupted_session(
                    runtime_state,
                    interrupted.partial_result,
                )
                return
            except (KeyboardInterrupt, EOFError):
                self.menu_action_dispatcher.handle_interrupted_program(runtime_state)
                return

    def _maximum_menu_choice(self, has_delete: bool) -> int:
        if has_delete:
            return c.MENU_MAX_CHOICE_WITH_DELETE
        return c.MENU_MAX_CHOICE_WITHOUT_DELETE
