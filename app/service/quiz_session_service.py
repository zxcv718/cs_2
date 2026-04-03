from typing import Optional

import app.config.constants as c
from app.model.quiz import Quiz
from app.service.quiz_partial_result_builder import QuizPartialResultBuilder
from app.service.quiz_question_round_service import (
    QuizQuestionRoundInterrupted,
    QuizQuestionRoundService,
)
from app.service.quiz_selection_service import QuizSelectionService
from app.service.quiz_session_models import QuizSessionInterrupted, QuizSessionResult
from app.ui.console_ui import ConsoleUI


# 퀴즈를 실제로 진행하는 서비스입니다.
class QuizSessionService:
    def __init__(
        self,
        ui: ConsoleUI,
        selection_service: Optional[QuizSelectionService] = None,
        question_round_service: Optional[QuizQuestionRoundService] = None,
        partial_result_builder: Optional[QuizPartialResultBuilder] = None,
    ) -> None:
        self.ui = ui
        self.selection_service = selection_service or QuizSelectionService(ui)
        self.question_round_service = question_round_service or QuizQuestionRoundService(
            ui
        )
        self.partial_result_builder = (
            partial_result_builder or QuizPartialResultBuilder()
        )

    # 퀴즈 플레이 한 번을 끝까지 진행하고 결과를 돌려줍니다.
    def play(self, quizzes: list[Quiz]) -> Optional[QuizSessionResult]:
        if not quizzes:
            self.ui.show_message(c.MESSAGE_NO_QUIZZES)
            return None

        # 문제 수를 고르고, 그 수만큼 랜덤으로 출제합니다.
        question_count = self.choose_question_count(len(quizzes))
        selected_quizzes = self._select_quizzes(quizzes, question_count)
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
                self._build_partial_result(
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

    def choose_question_count(self, total_questions: int) -> int:
        return self.selection_service.choose_question_count(total_questions)

    def _select_quizzes(self, quizzes: list[Quiz], question_count: int) -> list[Quiz]:
        return self.selection_service.select_quizzes(quizzes, question_count)

    def _build_partial_result(
        self,
        total_questions: int,
        correct_count: int,
        hint_used_count: int,
        answered_question_count: int,
    ) -> Optional[QuizSessionResult]:
        return self.partial_result_builder.build_interrupted_result(
            total_questions,
            correct_count,
            hint_used_count,
            answered_question_count,
        )
