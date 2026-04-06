import random

import app.config.constants as constants
from app.model.quiz import Quiz
from app.model.quiz_catalog import QuizCatalog
from app.service.quiz_metrics import QuestionCount
from app.ui.console_ui import ConsoleUI


class QuizSelectionService:
    def __init__(self, console_interface: ConsoleUI) -> None:
        self.console_interface = console_interface

    def show_no_quizzes(self) -> None:
        self.console_interface.show_message(constants.MESSAGE_NO_QUIZZES)

    def choose_question_count(self, total_questions: int) -> QuestionCount:
        return QuestionCount(
            self.console_interface.request_valid_number(
            constants.PROMPT_QUESTION_COUNT_TEMPLATE.format(count=total_questions),
            constants.DISPLAY_INDEX_START,
            total_questions,
        )
        )

    def select_quizzes(
        self,
        quiz_catalog: QuizCatalog,
        question_count: QuestionCount,
    ) -> list[Quiz]:
        return quiz_catalog.randomized_selection(question_count)
