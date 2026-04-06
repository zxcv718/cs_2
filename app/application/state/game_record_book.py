from dataclasses import dataclass

from app.application.play.best_score_service import BestScore, BestScoreUpdate
from app.application.state.game_history import GameHistory
from app.application.state.quiz_history_entry import QuizHistoryEntry


@dataclass
class GameRecordBook:
    best_score: BestScore
    play_history: GameHistory

    @classmethod
    def create_empty(cls) -> "GameRecordBook":
        return cls(BestScore.empty(), GameHistory())

    def record(self, best_score_update: BestScoreUpdate, history_entry: QuizHistoryEntry) -> None:
        self.best_score = best_score_update.best_score
        play_history = self.play_history
        play_history.append(history_entry)
