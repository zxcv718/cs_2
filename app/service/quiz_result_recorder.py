from dataclasses import dataclass

from app.service.game_runtime_state import GameRuntimeState
from app.service.quiz_history_service import QuizHistoryService
from app.service.quiz_score_keeper import QuizScoreKeeper
from app.service.quiz_session_models import QuizSessionResult


@dataclass(frozen=True)
class RecordedQuizResult:
    score: int
    best_score: int | None
    is_new_record: bool


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
        result: QuizSessionResult,
    ) -> RecordedQuizResult:
        score_record = self.score_keeper.keep(
            runtime_state.game_lifecycle.record_book.best_score,
            result,
        )
        runtime_state.record_play_result(
            score_record.best_score,
            self.history_service.create_entry(result, score_record.score),
        )
        return RecordedQuizResult(
            score_record.score,
            score_record.best_score,
            score_record.is_new_record,
        )
