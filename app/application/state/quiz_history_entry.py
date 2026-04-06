from dataclasses import dataclass

from app.application.play.quiz_session_models import QuizPerformance
from app.service.quiz_metrics import CorrectAnswerCount, HintUsageCount, PlayedAt, QuestionCount, ScoreValue


@dataclass(frozen=True)
class ScoredPerformance:
    _quiz_performance: QuizPerformance
    _score_value: ScoreValue

    def quiz_performance(self) -> QuizPerformance:
        return self._quiz_performance

    def score_value(self) -> ScoreValue:
        return self._score_value


@dataclass(frozen=True)
class QuizHistoryEntry:
    _played_at: PlayedAt
    _scored_performance: ScoredPerformance

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

    def played_at(self) -> PlayedAt:
        return self._played_at

    def question_count(self) -> QuestionCount:
        quiz_performance = self._quiz_performance()
        return quiz_performance.question_count()

    def correct_answers(self) -> CorrectAnswerCount:
        quiz_performance = self._quiz_performance()
        return quiz_performance.correct_answers()

    def hint_usages(self) -> HintUsageCount:
        quiz_performance = self._quiz_performance()
        return quiz_performance.hint_usages()

    def score_value(self) -> ScoreValue:
        scored_performance = self._scored_performance
        return scored_performance.score_value()

    def _quiz_performance(self) -> QuizPerformance:
        scored_performance = self._scored_performance
        return scored_performance.quiz_performance()
