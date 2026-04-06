import app.config.constants as constants
from app.application.play.quiz_session_models import QuizSessionResult
from app.service.quiz_metrics import CorrectAnswerCount, HintUsageCount, QuestionCount
from typing import Optional


class QuizPartialResultBuilder:
    def build_completed_result(
        self,
        total_questions: QuestionCount,
        correct_count: CorrectAnswerCount,
        hint_used_count: HintUsageCount,
    ) -> QuizSessionResult:
        return QuizSessionResult(
            total_questions=total_questions,
            correct_count=correct_count,
            hint_used_count=hint_used_count,
        )

    def build_interrupted_result(
        self,
        total_questions: QuestionCount,
        correct_count: CorrectAnswerCount,
        hint_used_count: HintUsageCount,
        answered_question_count: QuestionCount,
    ) -> Optional[QuizSessionResult]:
        if int(answered_question_count) < constants.DISPLAY_INDEX_START:
            return None

        return self.build_completed_result(
            total_questions,
            correct_count,
            hint_used_count,
        )
