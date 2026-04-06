from dataclasses import dataclass

from app.service.game_history import GameHistory
from app.service.quiz_metrics import ScoreValue


@dataclass
class GameRecordBook:
    best_score: ScoreValue | None
    history: GameHistory

    @classmethod
    def create_empty(cls) -> "GameRecordBook":
        return cls(None, GameHistory())

    def record(self, best_score: ScoreValue | None, history_entry: dict[str, object]) -> None:
        self.best_score = best_score
        history = self.history
        history.append(history_entry)
