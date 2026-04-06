from app.service.default_state_recovery import DefaultStateRecovery
from app.service.game_runtime_state import GameRuntimeState
from app.service.game_state_service import GameStateService
from app.console_interface import ConsoleInterface


class GameBootstrapService:
    def __init__(
        self,
        state_service: GameStateService,
        default_state_recovery: DefaultStateRecovery,
    ) -> None:
        self.state_service = state_service
        self.default_state_recovery = default_state_recovery

    def initialize(
        self,
        runtime_state: GameRuntimeState,
        console_interface: ConsoleInterface,
    ) -> None:
        state_service = self.state_service
        default_state_recovery = self.default_state_recovery
        show_message = console_interface.show_message
        show_error = console_interface.show_error
        try:
            state = state_service.load_state()
        except FileNotFoundError:
            state = default_state_recovery.recover_for_missing_file(show_message)
        except ValueError:
            state = default_state_recovery.recover_for_invalid_state(show_error)
        except OSError:
            state = default_state_recovery.recover_for_read_error(show_error)

        runtime_state.apply_loaded_state(state)
