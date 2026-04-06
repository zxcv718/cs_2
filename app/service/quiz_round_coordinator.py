from typing import Optional

import app.config.constants as constants
from app.model.quiz import Quiz
from app.service.quiz_metrics import (
    CorrectAnswerCount,
    DisplayIndex,
    HintUsageCount,
    QuestionCount,
)
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
        correct_count = CorrectAnswerCount(constants.INITIAL_CORRECT_COUNT)
        hint_used_count = HintUsageCount(constants.INITIAL_HINT_USED_COUNT)
        answered_question_count = QuestionCount(constants.INITIAL_CORRECT_COUNT)
        total_questions = QuestionCount(len(selected_quizzes))

        try:
            for raw_index, quiz in enumerate(
                selected_quizzes,
                start=constants.DISPLAY_INDEX_START,
            ):
                display_index = DisplayIndex(raw_index)
                question_round_service = self.question_round_service
                round_result = question_round_service.play_round(
                    quiz,
                    display_index,
                    total_questions,
                )
                correct_count = correct_count.add(round_result.correct_count)
                hint_used_count = hint_used_count.add(round_result.hint_used_count)
                answered_question_count = answered_question_count.incremented()
        except QuizQuestionRoundInterrupted as interrupted:
            hint_used_count = hint_used_count.add(interrupted.hint_used_count)
            partial_result_builder = self.partial_result_builder
            raise QuizSessionInterrupted(
                partial_result_builder.build_interrupted_result(
                    total_questions,
                    correct_count,
                    hint_used_count,
                    answered_question_count,
                )
            ) from interrupted

        partial_result_builder = self.partial_result_builder
        return partial_result_builder.build_completed_result(
            total_questions,
            correct_count,
            hint_used_count,
        )
