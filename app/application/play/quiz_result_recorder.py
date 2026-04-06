from dataclasses import dataclass

from app.application.play.quiz_history_service import QuizHistoryService
from app.application.play.quiz_score_keeper import QuizScoreKeeper
from app.application.play.quiz_score_keeper import ScoreOutcome
from app.application.play.quiz_session_models import QuizPerformance
from app.application.state.game_runtime_state import GameRuntimeState


class QuizResultRecorder:
    def __init__(
        self,
        score_keeper: QuizScoreKeeper,
        history_service: QuizHistoryService,
    ) -> None:
        self.score_keeper = score_keeper
        self.history_service = history_service

    def record(
        self,
        runtime_state: GameRuntimeState,
        result: QuizPerformance,
    ) -> ScoreOutcome:
        score_keeper = self.score_keeper
        record_book = runtime_state.record_book
        score_outcome = score_keeper.keep(
            record_book.best_score,
            result,
        )
        history_service = self.history_service
        history_entry = history_service.create_entry(
            result,
            score_outcome.score_value,
        )
        runtime_state.record_play_result(
            score_outcome.best_score_update,
            history_entry,
        )
        return score_outcome
