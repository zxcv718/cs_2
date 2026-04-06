from typing import NoReturn

import app.config.constants as constants
from app.application.play.quiz_partial_result_builder import QuizPartialResultBuilder
from app.application.play.quiz_question_round_service import (
    QuizQuestionRoundInterrupted,
    QuizQuestionRoundService,
)
from app.application.play.quiz_session_models import AnswerTally, QuizPerformance, QuizSessionInterrupted
from app.model.quiz import Quiz
from app.model.quiz_selection import QuizSelection
from app.service.quiz_metrics import (
    CorrectAnswerCount,
    DisplayIndex,
    QuestionCount,
)


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
        selected_quizzes: QuizSelection,
    ) -> QuizPerformance:
        total_questions = selected_quizzes.total_questions()
        answer_tally = AnswerTally.empty()
        answered_question_count = QuestionCount(constants.INITIAL_CORRECT_COUNT)
        for quiz in selected_quizzes:
            try:
                round_tally = self._round_result(
                    quiz,
                    total_questions,
                    answered_question_count,
                )
            except QuizQuestionRoundInterrupted as interrupted:
                self._interrupted_result(
                    total_questions,
                    answer_tally.add(self._hint_only_tally(interrupted)),
                    answered_question_count,
                    interrupted,
                )
            answer_tally = answer_tally.add(round_tally)
            answered_question_count = answered_question_count.incremented()
        return self._completed_result(
            total_questions,
            answer_tally,
        )

    def _round_result(
        self,
        quiz: Quiz,
        total_questions: QuestionCount,
        answered_question_count: QuestionCount,
    ) -> AnswerTally:
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
        answer_tally: AnswerTally,
    ) -> QuizPerformance:
        partial_result_builder = self.partial_result_builder
        return partial_result_builder.build_performance(
            total_questions,
            answer_tally,
        )

    def _interrupted_result(
        self,
        total_questions: QuestionCount,
        answer_tally: AnswerTally,
        answered_question_count: QuestionCount,
        interrupted: QuizQuestionRoundInterrupted,
    ) -> NoReturn:
        partial_result_builder = self.partial_result_builder
        raise QuizSessionInterrupted(
            partial_result_builder.build_interrupted_result(
                total_questions,
                answer_tally,
                answered_question_count,
            )
        ) from interrupted

    def _hint_only_tally(
        self,
        interrupted: QuizQuestionRoundInterrupted,
    ) -> AnswerTally:
        return AnswerTally(
            CorrectAnswerCount(constants.INITIAL_CORRECT_COUNT),
            interrupted.hint_used_count,
        )
