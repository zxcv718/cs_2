from dataclasses import dataclass
from typing import Optional

from app.service.game_history import GameHistory


@dataclass
class GameRecordBook:
    best_score: Optional[int]
    history: GameHistory

    @classmethod
    def create_empty(cls) -> "GameRecordBook":
        return cls(None, GameHistory())

    def record(self, best_score: Optional[int], history_entry: dict[str, object]) -> None:
        self.best_score = best_score
        self.history.append(history_entry)
