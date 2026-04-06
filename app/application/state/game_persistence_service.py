import app.config.constants as constants
from app.application.state.game_snapshot import GameSnapshot
from app.application.state.game_runtime_state import GameRuntimeState
from app.application.state.game_state_service import GameStateService
from app.console.interface import ConsoleInterface


class GamePersistenceService:
    def __init__(
        self,
        state_service: GameStateService,
        console_interface: ConsoleInterface,
    ) -> None:
        self.state_service = state_service
        self.console_interface = console_interface

    def save_runtime_state(self, runtime_state: GameRuntimeState) -> None:
        state_service = self.state_service
        console_interface = self.console_interface
        try:
            state_service.save_state(runtime_state.saveable_snapshot())
        except OSError:
            console_interface.show_error(constants.ERROR_STATE_SAVE)
            return

    def save_snapshot(self, game_snapshot: GameSnapshot) -> None:
        state_service = self.state_service
        console_interface = self.console_interface
        try:
            state_service.save_state(game_snapshot)
        except OSError:
            console_interface.show_error(constants.ERROR_STATE_SAVE)
