from typing import Optional

import app.config.constants as c
from app.model.quiz import Quiz
from app.service.quiz_partial_result_builder import QuizPartialResultBuilder
from app.service.quiz_question_round_service import (
    QuizQuestionRoundInterrupted,
    QuizQuestionRoundService,
)
from app.service.quiz_session_models import QuizSessionInterrupted, QuizSessionResult


class QuizRoundCoordinator:
    def __init__(
        self,
        question_round_service: QuizQuestionRoundService,
        partial_result_builder: QuizPartialResultBuilder,
    ) -> None:
        self.question_round_service = question_round_service
        self.partial_result_builder = partial_result_builder

    def play_selected_quizzes(
        self,
        selected_quizzes: list[Quiz],
    ) -> Optional[QuizSessionResult]:
        correct_count = c.INITIAL_CORRECT_COUNT
        hint_used_count = c.INITIAL_HINT_USED_COUNT
        answered_question_count = c.INITIAL_CORRECT_COUNT

        try:
            for index, quiz in enumerate(selected_quizzes, start=c.DISPLAY_INDEX_START):
                round_result = self.question_round_service.play_round(
                    quiz,
                    index,
                    len(selected_quizzes),
                )
                correct_count += round_result.correct_count
                hint_used_count += round_result.hint_used_count
                answered_question_count += c.DISPLAY_INDEX_START
        except QuizQuestionRoundInterrupted as interrupted:
            hint_used_count += interrupted.hint_used_count
            raise QuizSessionInterrupted(
                self.partial_result_builder.build_interrupted_result(
                    len(selected_quizzes),
                    correct_count,
                    hint_used_count,
                    answered_question_count,
                )
            ) from interrupted

        return self.partial_result_builder.build_completed_result(
            len(selected_quizzes),
            correct_count,
            hint_used_count,
        )
