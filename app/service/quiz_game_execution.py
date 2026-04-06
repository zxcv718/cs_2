import app.config.constants as constants
from app.service.game_bootstrap_service import GameBootstrapService
from app.service.game_runtime_state import GameRuntimeState
from app.service.menu_action_dispatcher import MenuActionDispatcher
from app.service.quiz_metrics import MenuChoice
from app.service.quiz_session_models import QuizSessionInterrupted
from app.console_interface import ConsoleInterface


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
        console_interface: ConsoleInterface,
    ) -> None:
        game_bootstrap_service = self.game_bootstrap_service
        runtime_state.initialize_with(game_bootstrap_service, console_interface)

    def persist_state(self, runtime_state: GameRuntimeState) -> None:
        menu_action_dispatcher = self.menu_action_dispatcher
        menu_action_dispatcher.persist(runtime_state)

    def run(
        self,
        runtime_state: GameRuntimeState,
        console_interface: ConsoleInterface,
    ) -> None:
        self.initialize_state(runtime_state, console_interface)
        has_delete = constants.ENABLE_DELETE_MENU
        maximum_menu_choice = self._maximum_menu_choice(has_delete)
        self._run_once(
            runtime_state,
            has_delete,
            maximum_menu_choice,
            console_interface,
        )

    def _run_once(
        self,
        runtime_state: GameRuntimeState,
        has_delete: bool,
        maximum_menu_choice: int,
        console_interface: ConsoleInterface,
    ) -> None:
        menu_action_dispatcher = self.menu_action_dispatcher
        try:
            should_continue = self._dispatched_once(
                runtime_state,
                has_delete,
                maximum_menu_choice,
                console_interface,
            )
        except QuizSessionInterrupted as interrupted:
            menu_action_dispatcher.handle_interrupted_session(
                runtime_state,
                interrupted.partial_result,
            )
            return
        except (KeyboardInterrupt, EOFError):
            menu_action_dispatcher.handle_interrupted_program(runtime_state)
            return
        if not should_continue:
            return
        self._run_once(
            runtime_state,
            has_delete,
            maximum_menu_choice,
            console_interface,
        )

    def _dispatched_once(
        self,
        runtime_state: GameRuntimeState,
        has_delete: bool,
        maximum_menu_choice: int,
        console_interface: ConsoleInterface,
    ) -> bool:
        menu_action_dispatcher = self.menu_action_dispatcher
        console_interface.show_menu(has_delete=has_delete)
        menu_choice = console_interface.request_menu_choice(
            constants.MENU_MIN_CHOICE,
            maximum_menu_choice,
        )
        return menu_action_dispatcher.dispatch(
            menu_choice,
            runtime_state,
            has_delete,
            console_interface,
        )

    def _maximum_menu_choice(self, has_delete: bool) -> int:
        if has_delete:
            return constants.MENU_MAX_CHOICE_WITH_DELETE
        return constants.MENU_MAX_CHOICE_WITHOUT_DELETE
