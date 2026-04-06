from typing import Any, Callable

import app.config.constants as c
from app.service.default_game_state_factory import DefaultGameStateFactory
from app.service.game_persistence_service import GamePersistenceService


class DefaultStateRecovery:
    def __init__(
        self,
        default_state_factory: DefaultGameStateFactory,
        persistence_service: GamePersistenceService,
    ) -> None:
        self.default_state_factory = default_state_factory
        self.persistence_service = persistence_service

    def recover_for_missing_file(self, notify: Callable[[str], None]) -> dict[str, Any]:
        return self._recover(notify, c.MESSAGE_STATE_FILE_MISSING, should_save=True)

    def recover_for_invalid_state(self, notify: Callable[[str], None]) -> dict[str, Any]:
        return self._recover(notify, c.ERROR_STATE_CORRUPTED, should_save=True)

    def recover_for_read_error(self, notify: Callable[[str], None]) -> dict[str, Any]:
        return self._recover(notify, c.ERROR_STATE_READ, should_save=False)

    def _recover(
        self,
        notify: Callable[[str], None],
        message: str,
        should_save: bool,
    ) -> dict[str, Any]:
        notify(message)
        state = self.default_state_factory.create_state()
        if not should_save:
            return state
        self.persistence_service.save_state_values(
            state[c.STATE_KEY_QUIZZES],
            state[c.STATE_KEY_BEST_SCORE],
            state[c.STATE_KEY_HISTORY],
        )
        return state
