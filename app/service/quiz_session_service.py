from typing import Optional

from app.model.quiz import Quiz
from app.model.quiz_catalog import QuizCatalog
from app.service.quiz_metrics import QuestionCount
from app.service.quiz_partial_result_builder import QuizPartialResultBuilder
from app.service.question_count_chooser import QuestionCountChooser
from app.service.quiz_question_round_service import QuizQuestionRoundService
from app.service.quiz_round_coordinator import QuizRoundCoordinator
from app.service.quiz_session_models import QuizSessionResult
from app.console_interface import ConsoleInterface


# 퀴즈를 실제로 진행하는 서비스입니다.
class QuizSessionService:
    def __init__(
        self,
        console_interface: ConsoleInterface,
        question_count_chooser: Optional[QuestionCountChooser] = None,
        question_round_service: Optional[QuizQuestionRoundService] = None,
        partial_result_builder: Optional[QuizPartialResultBuilder] = None,
    ) -> None:
        self.question_count_chooser = question_count_chooser or QuestionCountChooser(
            console_interface
        )
        self.quiz_round_coordinator = QuizRoundCoordinator(
            question_round_service or QuizQuestionRoundService(console_interface),
            partial_result_builder or QuizPartialResultBuilder(),
        )

    # 퀴즈 플레이 한 번을 끝까지 진행하고 결과를 돌려줍니다.
    def play(self, quiz_catalog: QuizCatalog) -> Optional[QuizSessionResult]:
        question_count_chooser = self.question_count_chooser
        quiz_round_coordinator = self.quiz_round_coordinator
        if not quiz_catalog:
            question_count_chooser.show_no_quizzes()
            return None

        # 문제 수를 고르고, 그 수만큼 랜덤으로 출제합니다.
        question_count = self.choose_question_count(len(quiz_catalog))
        selected_quizzes = self._select_quizzes(quiz_catalog, question_count)
        return quiz_round_coordinator.play_selected_quizzes(selected_quizzes)

    def choose_question_count(self, total_questions: int) -> QuestionCount:
        question_count_chooser = self.question_count_chooser
        return question_count_chooser.choose_question_count(total_questions)

    def _select_quizzes(
        self,
        quiz_catalog: QuizCatalog,
        question_count: QuestionCount,
    ) -> list[Quiz]:
        return quiz_catalog.randomized_selection(question_count)
