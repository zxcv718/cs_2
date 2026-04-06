from app.application.play.best_score_service import BestScore
from app.application.state.game_runtime_state import GameRuntimeState
from app.console.interface import ConsoleInterface


class BestScoreDisplayService:
    def show(
        self,
        console_interface: ConsoleInterface,
        runtime_state: GameRuntimeState,
    ) -> None:
        record_book = runtime_state.record_book
        best_score = record_book.best_score
        display_score = self._score_value_or_none(best_score)
        console_interface.display_best_score(display_score)

    def _score_value_or_none(self, best_score: BestScore) -> int | None:
        score_value = best_score.score_value
        if score_value is None:
            return None
        return int(score_value)
