import random

import app.config.constants as c
from app.model.quiz import Quiz
from app.ui.console_ui import ConsoleUI


class QuizSelectionService:
    def __init__(self, ui: ConsoleUI) -> None:
        self.ui = ui

    def choose_question_count(self, total_questions: int) -> int:
        return self.ui.get_valid_number(
            c.PROMPT_QUESTION_COUNT_TEMPLATE.format(count=total_questions),
            c.DISPLAY_INDEX_START,
            total_questions,
        )

    def select_quizzes(self, quizzes: list[Quiz], question_count: int) -> list[Quiz]:
        working_quizzes = list(quizzes)
        random.shuffle(working_quizzes)
        return working_quizzes[:question_count]
