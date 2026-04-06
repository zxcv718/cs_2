from dataclasses import dataclass
from typing import Optional

from app.service.best_score_service import BestScoreService
from app.service.quiz_scoring_service import QuizScoringService
from app.service.quiz_session_models import QuizSessionResult


@dataclass(frozen=True)
class ScoreRecord:
    score: int
    best_score: Optional[int]
    is_new_record: bool


class QuizScoreKeeper:
    def __init__(
        self,
        scoring_service: QuizScoringService,
        best_score_service: BestScoreService,
    ) -> None:
        self.scoring_service = scoring_service
        self.best_score_service = best_score_service

    def keep(
        self,
        best_score: Optional[int],
        result: QuizSessionResult,
    ) -> ScoreRecord:
        score = self.scoring_service.calculate_score(
            result.correct_count,
            result.hint_used_count,
        )
        updated_best_score, is_new_record = self.best_score_service.update_best_score(
            best_score,
            score,
        )
        return ScoreRecord(score, updated_best_score, is_new_record)
