import app.config.constants as c
from app.model.quiz import Quiz
from app.ui.console_ui import ConsoleUI


# 퀴즈 추가, 목록 보기, 삭제를 담당하는 서비스입니다.
class QuizCatalogService:
    def __init__(self, ui: ConsoleUI) -> None:
        self.ui = ui

    # 새 퀴즈 정보를 입력받아 목록에 추가합니다.
    def add_quiz(self, quizzes: list[Quiz]) -> bool:
        question = self.ui.get_non_empty_text(c.PROMPT_ENTER_QUESTION)
        choices = [
            self.ui.get_non_empty_text(c.PROMPT_ENTER_CHOICE_TEMPLATE.format(index=index))
            for index in range(c.DISPLAY_INDEX_START, c.CHOICE_COUNT + c.DISPLAY_INDEX_START)
        ]
        answer = self.ui.get_valid_number(
            c.PROMPT_ENTER_ANSWER_TEMPLATE.format(
                min_answer=c.MIN_ANSWER,
                max_answer=c.MAX_ANSWER,
            ),
            c.MIN_ANSWER,
            c.MAX_ANSWER,
        )

        hint = None
        if self.ui.get_yes_no(c.PROMPT_ADD_HINT_CONFIRM):
            hint = self.ui.get_non_empty_text(c.PROMPT_ENTER_HINT)

        quizzes.append(Quiz(question, choices, answer, hint=hint))
        self.ui.show_message(c.MESSAGE_QUIZ_ADDED)
        return True

    # 퀴즈 전체 목록을 화면에 보여줍니다.
    def list_quizzes(self, quizzes: list[Quiz]) -> None:
        self.ui.show_quiz_list(quizzes)

    # 사용자가 고른 번호의 퀴즈를 삭제합니다.
    def delete_quiz(self, quizzes: list[Quiz]) -> bool:
        if not quizzes:
            self.ui.show_message(c.MESSAGE_NO_QUIZZES_TO_DELETE)
            return False

        self.ui.show_quiz_list(quizzes)
        index = self.ui.get_valid_number(
            c.PROMPT_DELETE_INDEX_TEMPLATE.format(count=len(quizzes)),
            c.DISPLAY_INDEX_START,
            len(quizzes),
        )

        if not self.ui.get_yes_no(c.PROMPT_DELETE_CONFIRM):
            self.ui.show_message(c.MESSAGE_DELETE_CANCELLED)
            return False

        removed_quiz = quizzes.pop(index - c.DISPLAY_INDEX_START)
        self.ui.show_message(
            c.MESSAGE_DELETE_SUCCESS_TEMPLATE.format(question=removed_quiz.question)
        )
        return True
