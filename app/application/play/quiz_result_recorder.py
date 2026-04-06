from dataclasses import dataclass

from app.application.play.quiz_history_service import QuizHistoryService
from app.application.play.quiz_score_keeper import QuizScoreKeeper
from app.application.play.quiz_session_models import QuizSessionResult
from app.application.state.game_runtime_state import GameRuntimeState
from app.service.quiz_metrics import ScoreValue


@dataclass(frozen=True)
class RecordedQuizResult:
    score: ScoreValue
    best_score: ScoreValue | None
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
        score_keeper = self.score_keeper
        game_lifecycle = runtime_state.game_lifecycle
        record_book = game_lifecycle.record_book
        score_record = score_keeper.keep(
            record_book.best_score,
            result,
        )
        history_service = self.history_service
        history_entry = history_service.create_entry(result, score_record.score)
        runtime_state.record_play_result(score_record.best_score, history_entry)
        return RecordedQuizResult(
            score_record.score,
            score_record.best_score,
            score_record.is_new_record,
        )
