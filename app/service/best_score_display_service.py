from app.console_interface import ConsoleInterface
from app.service.game_runtime_state import GameRuntimeState
from app.service.quiz_metrics import ScoreValue


class BestScoreDisplayService:
    def show(
        self,
        console_interface: ConsoleInterface,
        runtime_state: GameRuntimeState,
    ) -> None:
        game_lifecycle = runtime_state.game_lifecycle
        record_book = game_lifecycle.record_book
        best_score = record_book.best_score
        display_score = self._score_value_or_none(best_score)
        console_interface.display_best_score(display_score)

    def _score_value_or_none(self, score_value: ScoreValue | None) -> int | None:
        if score_value is None:
            return None
        return int(score_value)
