import app.config.constants as constants
from app.application.menu_action_dispatcher import MenuActionDispatcher
from app.application.play.quiz_session_models import QuizSessionInterrupted
from app.application.state.game_bootstrap_service import GameBootstrapService
from app.application.state.game_runtime_state import GameRuntimeState
from app.console.interface import ConsoleInterface
from app.service.quiz_metrics import DeleteMenuAvailability


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
        game_bootstrap_service.initialize(runtime_state, console_interface)

    def persist_state(self, runtime_state: GameRuntimeState) -> None:
        menu_action_dispatcher = self.menu_action_dispatcher
        menu_action_dispatcher.persist(runtime_state)

    def run(
        self,
        runtime_state: GameRuntimeState,
        console_interface: ConsoleInterface,
    ) -> None:
        self.initialize_state(runtime_state, console_interface)
        delete_menu_availability = DeleteMenuAvailability.configured()
        maximum_menu_choice = delete_menu_availability.maximum_menu_choice()
        menu_action_dispatcher = self.menu_action_dispatcher
        while True:
            try:
                should_continue = self._dispatched_once(
                    runtime_state,
                    delete_menu_availability,
                    maximum_menu_choice,
                    console_interface,
                )
            except QuizSessionInterrupted as interrupted:
                menu_action_dispatcher.handle_interrupted_session(
                    runtime_state,
                    interrupted.partial_performance,
                )
                return
            except (KeyboardInterrupt, EOFError):
                menu_action_dispatcher.handle_interrupted_program(runtime_state)
                return
            if not should_continue:
                return

    def _dispatched_once(
        self,
        runtime_state: GameRuntimeState,
        delete_menu_availability: DeleteMenuAvailability,
        maximum_menu_choice: int,
        console_interface: ConsoleInterface,
    ) -> bool:
        menu_action_dispatcher = self.menu_action_dispatcher
        console_interface.show_menu(delete_menu_availability)
        menu_choice = console_interface.request_menu_choice(
            constants.MENU_MIN_CHOICE,
            maximum_menu_choice,
        )
        return menu_action_dispatcher.dispatch(
            menu_choice,
            runtime_state,
            delete_menu_availability,
            console_interface,
        )
