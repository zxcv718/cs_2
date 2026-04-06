from dataclasses import dataclass

from app.application.play.best_score_service import BestScore, BestScoreService, BestScoreUpdate
from app.application.play.quiz_scoring_service import QuizScoringService
from app.application.play.quiz_session_models import QuizPerformance
from app.service.quiz_metrics import ScoreValue


@dataclass(frozen=True)
class ScoreOutcome:
    score_value: ScoreValue
    best_score_update: BestScoreUpdate


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
        best_score: BestScore,
        result: QuizPerformance,
    ) -> ScoreOutcome:
        scoring_service = self.scoring_service
        answer_tally = result.answer_tally
        score = scoring_service.calculate_score(
            answer_tally.correct_answers,
            answer_tally.hint_usages,
        )
        best_score_service = self.best_score_service
        best_score_update = best_score_service.update_best_score(
            best_score,
            score,
        )
        return ScoreOutcome(score, best_score_update)
