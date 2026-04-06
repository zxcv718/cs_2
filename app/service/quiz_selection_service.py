import random

import app.config.constants as constants
from app.model.quiz import Quiz
from app.model.quiz_catalog import QuizCatalog
from app.service.quiz_metrics import QuestionCount
from app.console_interface import ConsoleInterface


class QuizSelectionService:
    def __init__(self, console_interface: ConsoleInterface) -> None:
        self.console_interface = console_interface

    def show_no_quizzes(self) -> None:
        console_interface = self.console_interface
        console_interface.show_message(constants.MESSAGE_NO_QUIZZES)

    def choose_question_count(self, total_questions: int) -> QuestionCount:
        console_interface = self.console_interface
        prompt_template = constants.PROMPT_QUESTION_COUNT_TEMPLATE
        prompt = prompt_template.format(count=total_questions)
        question_count = console_interface.request_valid_number(
            prompt,
            constants.DISPLAY_INDEX_START,
            total_questions,
        )
        return QuestionCount(question_count)

    def select_quizzes(
        self,
        quiz_catalog: QuizCatalog,
        question_count: QuestionCount,
    ) -> list[Quiz]:
        return quiz_catalog.randomized_selection(question_count)
