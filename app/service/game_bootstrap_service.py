from app.service.default_state_recovery import DefaultStateRecovery
from app.service.game_runtime_state import GameRuntimeState
from app.service.game_state_service import GameStateService
from app.ui.console_ui import ConsoleUI


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
        console_interface: ConsoleUI,
    ) -> None:
        try:
            state = self.state_service.load_state()
        except FileNotFoundError:
            state = self.default_state_recovery.recover_for_missing_file(
                console_interface.show_message
            )
        except ValueError:
            state = self.default_state_recovery.recover_for_invalid_state(
                console_interface.show_error
            )
        except OSError:
            state = self.default_state_recovery.recover_for_read_error(
                console_interface.show_error
            )

        runtime_state.apply_loaded_state(state)
