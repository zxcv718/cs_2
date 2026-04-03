from typing import Any, Callable

import app.config.constants as c
from app.service.default_game_state_factory import DefaultGameStateFactory
from app.service.game_persistence_service import GamePersistenceService
from app.service.game_runtime_state import GameRuntimeState
from app.service.game_state_service import GameStateService
from app.ui.console_ui import ConsoleUI


class GameBootstrapService:
    def __init__(
        self,
        ui: ConsoleUI,
        state_service: GameStateService,
        default_state_factory: DefaultGameStateFactory,
        persistence_service: GamePersistenceService,
    ) -> None:
        self.ui = ui
        self.state_service = state_service
        self.default_state_factory = default_state_factory
        self.persistence_service = persistence_service

    def initialize(self, runtime_state: GameRuntimeState) -> None:
        try:
            state = self.state_service.load_state()
        except FileNotFoundError:
            state = self._recover_with_default_state(
                self.ui.show_message,
                c.MESSAGE_STATE_FILE_MISSING,
                should_save=True,
            )
        except ValueError:
            state = self._recover_with_default_state(
                self.ui.show_error,
                c.ERROR_STATE_CORRUPTED,
                should_save=True,
            )
        except OSError:
            state = self._recover_with_default_state(
                self.ui.show_error,
                c.ERROR_STATE_READ,
                should_save=False,
            )

        runtime_state.apply_loaded_state(state)

    def _recover_with_default_state(
        self,
        notify: Callable[[str], None],
        message: str,
        should_save: bool,
    ) -> dict[str, Any]:
        notify(message)
        state = self.default_state_factory.create_state()
        if should_save:
            self.persistence_service.save_state_values(
                state[c.STATE_KEY_QUIZZES],
                state[c.STATE_KEY_BEST_SCORE],
                state[c.STATE_KEY_HISTORY],
            )
        return state
