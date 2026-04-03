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

    def apply_loaded_state(self, state: dict[str, Any]) -> None:
        self.quizzes = state[c.STATE_KEY_QUIZZES]
        self.best_score = state[c.STATE_KEY_BEST_SCORE]
        self.history = state.get(c.STATE_KEY_HISTORY, [])
        self.initialized = True
