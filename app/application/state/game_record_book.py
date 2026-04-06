from dataclasses import dataclass

from app.application.play.best_score_service import BestScore, BestScoreUpdate
from app.application.state.game_history import GameHistory
from app.application.state.quiz_history_entry import QuizHistoryEntry


@dataclass
class GameRecordBook:
    _best_score: BestScore
    _history: GameHistory

    @classmethod
    def create_empty(cls) -> "GameRecordBook":
        return cls(BestScore.empty(), GameHistory())

    def record(self, best_score_update: BestScoreUpdate, history_entry: QuizHistoryEntry) -> None:
        self._best_score = best_score_update.best_score()
        history = self._history
        history.append(history_entry)

    def current_best_score(self) -> BestScore:
        return self._best_score

    def play_history(self) -> GameHistory:
        return self._history
