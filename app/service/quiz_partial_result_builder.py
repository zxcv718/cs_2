import app.config.constants as c
from app.service.quiz_session_models import QuizSessionResult
from typing import Optional


class QuizPartialResultBuilder:
    def build_completed_result(
        self,
        total_questions: int,
        correct_count: int,
        hint_used_count: int,
    ) -> QuizSessionResult:
        return QuizSessionResult(
            total_questions=total_questions,
            correct_count=correct_count,
            hint_used_count=hint_used_count,
        )

    def build_interrupted_result(
        self,
        total_questions: int,
        correct_count: int,
        hint_used_count: int,
        answered_question_count: int,
    ) -> Optional[QuizSessionResult]:
        if answered_question_count < c.DISPLAY_INDEX_START:
            return None

        return self.build_completed_result(
            total_questions,
            correct_count,
            hint_used_count,
        )
