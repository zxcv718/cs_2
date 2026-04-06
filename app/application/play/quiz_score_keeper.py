from dataclasses import dataclass

from app.application.play.best_score_service import BestScore, BestScoreService, BestScoreUpdate
from app.application.play.quiz_scoring_service import QuizScoringService
from app.application.play.quiz_session_models import QuizPerformance
from app.service.quiz_metrics import ScoreValue


@dataclass(frozen=True)
class ScoreOutcome:
    _score: ScoreValue
    _best_score_update: BestScoreUpdate

    def score_value(self) -> ScoreValue:
        return self._score

    def best_score_update(self) -> BestScoreUpdate:
        return self._best_score_update

    def record_update_status(self):
        best_score_update = self._best_score_update
        return best_score_update.record_status()


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
        score = scoring_service.calculate_score(
            result.correct_answers(),
            result.hint_usages(),
        )
        best_score_service = self.best_score_service
        best_score_update = best_score_service.update_best_score(
            best_score,
            score,
        )
        return ScoreOutcome(score, best_score_update)
