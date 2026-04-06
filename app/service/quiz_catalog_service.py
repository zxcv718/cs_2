import app.config.constants as c
from app.model.quiz import Quiz
from app.model.quiz_catalog import QuizCatalog
from app.model.quiz_factory import QuizFactory
from app.ui.console_ui import ConsoleUI
from typing import Optional


# 퀴즈 추가, 목록 보기, 삭제를 담당하는 서비스입니다.
class QuizCatalogService:
    def __init__(
        self,
        console_interface: ConsoleUI,
        quiz_factory: Optional[QuizFactory] = None,
    ) -> None:
        self.console_interface = console_interface
        self.quiz_factory = quiz_factory or QuizFactory()

    # 새 퀴즈 정보를 입력받아 목록에 추가합니다.
    def add_quiz(self, quiz_catalog: QuizCatalog) -> bool:
        question = self.console_interface.get_non_empty_text(c.PROMPT_ENTER_QUESTION)
        choices = [
            self.console_interface.get_non_empty_text(
                c.PROMPT_ENTER_CHOICE_TEMPLATE.format(index=index)
            )
            for index in range(c.DISPLAY_INDEX_START, c.CHOICE_COUNT + c.DISPLAY_INDEX_START)
        ]
        answer = self.console_interface.get_valid_number(
            c.PROMPT_ENTER_ANSWER_TEMPLATE.format(
                min_answer=c.MIN_ANSWER,
                max_answer=c.MAX_ANSWER,
            ),
            c.MIN_ANSWER,
            c.MAX_ANSWER,
        )

        hint = None
        if self.console_interface.get_yes_no(c.PROMPT_ADD_HINT_CONFIRM):
            hint = self.console_interface.get_non_empty_text(c.PROMPT_ENTER_HINT)

        quiz_catalog.append(self.quiz_factory.create(question, choices, answer, hint=hint))
        self.console_interface.show_message(c.MESSAGE_QUIZ_ADDED)
        return True

    # 퀴즈 전체 목록을 화면에 보여줍니다.
    def list_quizzes(self, quiz_catalog: QuizCatalog) -> None:
        self.console_interface.show_quiz_list(quiz_catalog)

    # 사용자가 고른 번호의 퀴즈를 삭제합니다.
    def delete_quiz(self, quiz_catalog: QuizCatalog) -> bool:
        if not quiz_catalog.has_items():
            self.console_interface.show_message(c.MESSAGE_NO_QUIZZES_TO_DELETE)
            return False

        self.console_interface.show_quiz_list(quiz_catalog)
        index = self.console_interface.get_valid_number(
            c.PROMPT_DELETE_INDEX_TEMPLATE.format(count=quiz_catalog.display_count()),
            c.DISPLAY_INDEX_START,
            quiz_catalog.display_count(),
        )

        if not self.console_interface.get_yes_no(c.PROMPT_DELETE_CONFIRM):
            self.console_interface.show_message(c.MESSAGE_DELETE_CANCELLED)
            return False

        removed_quiz = quiz_catalog.remove_by_display_index(index)
        self.console_interface.show_message(
            c.MESSAGE_DELETE_SUCCESS_TEMPLATE.format(
                question=removed_quiz.payload_item()[c.QUIZ_FIELD_QUESTION]
            )
        )
        return True
