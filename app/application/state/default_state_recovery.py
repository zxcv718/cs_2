from dataclasses import dataclass
from typing import Callable

import app.config.constants as constants
from app.application.state.default_game_state_factory import DefaultGameStateFactory
from app.application.state.game_persistence_service import GamePersistenceService
from app.application.state.game_snapshot import GameSnapshot
from app.application.state.game_state_service import GameStateService


@dataclass(frozen=True)
class PersistenceDecision:
    _requires_save: bool

    @classmethod
    def save(cls) -> "PersistenceDecision":
        return cls(True)

    @classmethod
    def skip(cls) -> "PersistenceDecision":
        return cls(False)

    def requires_save(self) -> bool:
        return self._requires_save


@dataclass(frozen=True)
class RecoveryPlan:
    _game_snapshot: GameSnapshot
    _persistence_decision: PersistenceDecision

    def game_snapshot(self) -> GameSnapshot:
        return self._game_snapshot

    def persistence_decision(self) -> PersistenceDecision:
        return self._persistence_decision


class StateRecoveryPolicy:
    def __init__(
        self,
        default_state_factory: DefaultGameStateFactory,
        state_service: GameStateService,
    ) -> None:
        self.default_state_factory = default_state_factory
        self.state_service = state_service

    def missing_file_plan(self) -> RecoveryPlan:
        return RecoveryPlan(
            self.default_state_factory.create_state(),
            PersistenceDecision.save(),
        )

    def invalid_state_plan(self) -> RecoveryPlan:
        persistence_decision = self._backup_decision()
        return RecoveryPlan(
            self.default_state_factory.create_state(),
            persistence_decision,
        )

    def read_error_plan(self) -> RecoveryPlan:
        return RecoveryPlan(
            self.default_state_factory.create_state(),
            PersistenceDecision.skip(),
        )

    def _backup_decision(self) -> PersistenceDecision:
        state_service = self.state_service
        try:
            if state_service.backup_state_file() is None:
                return PersistenceDecision.skip()
            return PersistenceDecision.save()
        except OSError:
            return PersistenceDecision.skip()


class StateRecoveryPersistence:
    def __init__(self, persistence_service: GamePersistenceService) -> None:
        self.persistence_service = persistence_service

    def apply(self, recovery_plan: RecoveryPlan) -> GameSnapshot:
        persistence_decision = recovery_plan.persistence_decision()
        if persistence_decision.requires_save():
            self.persistence_service.save_snapshot(recovery_plan.game_snapshot())
        return recovery_plan.game_snapshot()


class DefaultStateRecovery:
    def __init__(
        self,
        recovery_policy: StateRecoveryPolicy,
        recovery_persistence: StateRecoveryPersistence,
    ) -> None:
        self.recovery_policy = recovery_policy
        self.recovery_persistence = recovery_persistence

    def recover_for_missing_file(self, notify: Callable[[str], None]) -> GameSnapshot:
        notify(constants.MESSAGE_STATE_FILE_MISSING)
        recovery_policy = self.recovery_policy
        recovery_plan = recovery_policy.missing_file_plan()
        return self.recovery_persistence.apply(recovery_plan)

    def recover_for_invalid_state(self, notify: Callable[[str], None]) -> GameSnapshot:
        notify(constants.ERROR_STATE_CORRUPTED)
        recovery_policy = self.recovery_policy
        recovery_plan = recovery_policy.invalid_state_plan()
        return self.recovery_persistence.apply(recovery_plan)

    def recover_for_read_error(self, notify: Callable[[str], None]) -> GameSnapshot:
        notify(constants.ERROR_STATE_READ)
        recovery_policy = self.recovery_policy
        recovery_plan = recovery_policy.read_error_plan()
        return self.recovery_persistence.apply(recovery_plan)
