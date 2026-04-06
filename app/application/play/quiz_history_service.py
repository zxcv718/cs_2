from app.application.play.quiz_session_models import QuizPerformance
from app.application.state.quiz_history_entry import QuizHistoryEntry
from app.service.quiz_metrics import PlayedAt, ScoreValue


class QuizHistoryService:
    def create_entry(
        self,
        quiz_performance: QuizPerformance,
        score_value: ScoreValue,
    ) -> QuizHistoryEntry:
        return QuizHistoryEntry.create_now(quiz_performance, score_value)

    def restore_entry(
        self,
        played_at: PlayedAt,
        quiz_performance: QuizPerformance,
        score_value: ScoreValue,
    ) -> QuizHistoryEntry:
        return QuizHistoryEntry.restore(
            played_at,
            quiz_performance,
            score_value,
        )
