from typing import Any, Callable

import app.config.constants as constants
from app.application.state.default_game_state_factory import DefaultGameStateFactory
from app.application.state.game_persistence_service import GamePersistenceService


class DefaultStateRecovery:
    def __init__(
        self,
        default_state_factory: DefaultGameStateFactory,
        persistence_service: GamePersistenceService,
    ) -> None:
        self.default_state_factory = default_state_factory
        self.persistence_service = persistence_service

    def recover_for_missing_file(self, notify: Callable[[str], None]) -> dict[str, Any]:
        return self._recover(
            notify,
            constants.MESSAGE_STATE_FILE_MISSING,
            should_save=True,
        )

    def recover_for_invalid_state(self, notify: Callable[[str], None]) -> dict[str, Any]:
        return self._recover(
            notify,
            constants.ERROR_STATE_CORRUPTED,
            should_save=True,
        )

    def recover_for_read_error(self, notify: Callable[[str], None]) -> dict[str, Any]:
        return self._recover(
            notify,
            constants.ERROR_STATE_READ,
            should_save=False,
        )

    def _recover(
        self,
        notify: Callable[[str], None],
        message: str,
        should_save: bool,
    ) -> dict[str, Any]:
        notify(message)
        default_state_factory = self.default_state_factory
        state = default_state_factory.create_state()
        if not should_save:
            return state
        persistence_service = self.persistence_service
        persistence_service.save_state_values(
            state[constants.STATE_KEY_QUIZZES],
            state[constants.STATE_KEY_BEST_SCORE],
            state[constants.STATE_KEY_HISTORY],
        )
        return state
