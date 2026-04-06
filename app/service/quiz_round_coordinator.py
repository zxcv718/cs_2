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
    QuizQuestionRoundResult,
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
        total_questions = QuestionCount(len(selected_quizzes))
        correct_count = CorrectAnswerCount(constants.INITIAL_CORRECT_COUNT)
        hint_used_count = HintUsageCount(constants.INITIAL_HINT_USED_COUNT)
        answered_question_count = QuestionCount(constants.INITIAL_CORRECT_COUNT)
        return self._played_result(
            selected_quizzes,
            total_questions,
            correct_count,
            hint_used_count,
            answered_question_count,
        )

    def _played_result(
        self,
        selected_quizzes: list[Quiz],
        total_questions: QuestionCount,
        correct_count: CorrectAnswerCount,
        hint_used_count: HintUsageCount,
        answered_question_count: QuestionCount,
    ) -> QuizSessionResult:
        if not selected_quizzes:
            return self._completed_result(
                total_questions,
                correct_count,
                hint_used_count,
            )
        quiz = selected_quizzes[0]
        remaining_quizzes = selected_quizzes[1:]
        try:
            round_result = self._round_result(
                quiz,
                total_questions,
                answered_question_count,
            )
        except QuizQuestionRoundInterrupted as interrupted:
            return self._interrupted_result(
                total_questions,
                correct_count,
                hint_used_count.add(interrupted.hint_used_count),
                answered_question_count,
                interrupted,
            )
        return self._played_result(
            remaining_quizzes,
            total_questions,
            correct_count.add(round_result.correct_count),
            hint_used_count.add(round_result.hint_used_count),
            answered_question_count.incremented(),
        )

    def _round_result(
        self,
        quiz: Quiz,
        total_questions: QuestionCount,
        answered_question_count: QuestionCount,
    ) -> QuizQuestionRoundResult:
        question_round_service = self.question_round_service
        display_index = DisplayIndex(int(answered_question_count) + constants.DISPLAY_INDEX_START)
        return question_round_service.play_round(
            quiz,
            display_index,
            total_questions,
        )

    def _completed_result(
        self,
        total_questions: QuestionCount,
        correct_count: CorrectAnswerCount,
        hint_used_count: HintUsageCount,
    ) -> QuizSessionResult:
        partial_result_builder = self.partial_result_builder
        return partial_result_builder.build_completed_result(
            total_questions,
            correct_count,
            hint_used_count,
        )

    def _interrupted_result(
        self,
        total_questions: QuestionCount,
        correct_count: CorrectAnswerCount,
        hint_used_count: HintUsageCount,
        answered_question_count: QuestionCount,
        interrupted: QuizQuestionRoundInterrupted,
    ) -> QuizSessionResult:
        partial_result_builder = self.partial_result_builder
        raise QuizSessionInterrupted(
            partial_result_builder.build_interrupted_result(
                total_questions,
                correct_count,
                hint_used_count,
                answered_question_count,
            )
        ) from interrupted
