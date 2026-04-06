from dataclasses import dataclass

from app.application.play.quiz_session_models import QuizPerformance
from app.service.quiz_metrics import CorrectAnswerCount, HintUsageCount, PlayedAt, QuestionCount, ScoreValue


@dataclass(frozen=True)
class ScoredPerformance:
    quiz_performance: QuizPerformance
    score_value: ScoreValue


@dataclass(frozen=True)
class QuizHistoryEntry:
    played_at: PlayedAt
    scored_performance: ScoredPerformance

    @classmethod
    def create_now(
        cls,
        quiz_performance: QuizPerformance,
        score_value: ScoreValue,
    ) -> "QuizHistoryEntry":
        return cls(
            PlayedAt.now(),
            ScoredPerformance(quiz_performance, score_value),
        )

    @classmethod
    def restore(
        cls,
        played_at: PlayedAt,
        quiz_performance: QuizPerformance,
        score_value: ScoreValue,
    ) -> "QuizHistoryEntry":
        return cls(
            played_at,
            ScoredPerformance(quiz_performance, score_value),
        )
