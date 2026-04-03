from dataclasses import dataclass

from app.service.best_score_service import BestScoreService
from app.service.game_runtime_state import GameRuntimeState
from app.service.quiz_history_service import QuizHistoryService
from app.service.quiz_scoring_service import QuizScoringService
from app.service.quiz_session_service import QuizSessionResult


@dataclass(frozen=True)
class RecordedQuizResult:
    score: int
    is_new_record: bool


class QuizResultRecorder:
    def __init__(
        self,
        scoring_service: QuizScoringService,
        best_score_service: BestScoreService,
        history_service: QuizHistoryService,
    ) -> None:
        self.scoring_service = scoring_service
        self.best_score_service = best_score_service
        self.history_service = history_service

    def record(
        self,
        runtime_state: GameRuntimeState,
        result: QuizSessionResult,
    ) -> RecordedQuizResult:
        score = self.scoring_service.calculate_score(
            result.correct_count,
            result.hint_used_count,
        )
        runtime_state.best_score, is_new_record = (
            self.best_score_service.update_best_score(
                runtime_state.best_score,
                score,
            )
        )
        runtime_state.history.append(self.history_service.create_entry(result, score))
        return RecordedQuizResult(score, is_new_record)
