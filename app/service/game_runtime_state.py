from dataclasses import dataclass, field
from typing import Any, Optional

import app.config.constants as c
from app.model.quiz import Quiz


@dataclass
class GameRuntimeState:
    quizzes: list[Quiz] = field(default_factory=list)
    best_score: Optional[int] = None
    history: list[dict[str, Any]] = field(default_factory=list)
    initialized: bool = False

    def is_initialized(self) -> bool:
        return self.initialized

    def restore(
        self,
        quizzes: list[Quiz],
        best_score: Optional[int],
        history: list[dict[str, Any]],
    ) -> None:
        self.quizzes = quizzes
        self.best_score = best_score
        self.history = history
        self.initialized = True

    def apply_loaded_state(self, state: dict[str, Any]) -> None:
        self.restore(
            state[c.STATE_KEY_QUIZZES],
            state[c.STATE_KEY_BEST_SCORE],
            state.get(c.STATE_KEY_HISTORY, []),
        )

    def record_play_result(
        self,
        best_score: Optional[int],
        history_entry: dict[str, Any],
    ) -> None:
        self.best_score = best_score
        self.history.append(history_entry)
