import app.config.constants as constants
from app.model.quiz import Quiz
from app.model.quiz_catalog import QuizCatalog
from app.model.quiz_factory import QuizFactory
from app.service.quiz_metrics import DisplayIndex
from app.console_interface import ConsoleInterface
from typing import Optional


# 퀴즈 추가, 목록 보기, 삭제를 담당하는 서비스입니다.
class QuizCatalogService:
    def __init__(
        self,
        console_interface: ConsoleInterface,
        quiz_factory: Optional[QuizFactory] = None,
    ) -> None:
        self.console_interface = console_interface
        self.quiz_factory = quiz_factory or QuizFactory()

    # 새 퀴즈 정보를 입력받아 목록에 추가합니다.
    def add_quiz(self, quiz_catalog: QuizCatalog) -> bool:
        console_interface = self.console_interface
        quiz_factory = self.quiz_factory
        question_prompt = constants.PROMPT_ENTER_QUESTION
        question = console_interface.request_non_empty_text(question_prompt)
        choices = self._choices(console_interface)
        answer_prompt = self._answer_prompt()
        answer = console_interface.request_valid_number(
            answer_prompt,
            constants.MIN_ANSWER,
            constants.MAX_ANSWER,
        )

        hint = None
        hint_confirm_prompt = constants.PROMPT_ADD_HINT_CONFIRM
        if console_interface.request_yes_no(hint_confirm_prompt):
            hint_prompt = constants.PROMPT_ENTER_HINT
            hint = console_interface.request_non_empty_text(hint_prompt)

        created_quiz = quiz_factory.create(question, choices, answer, hint=hint)
        quiz_catalog.append(created_quiz)
        added_message = constants.MESSAGE_QUIZ_ADDED
        console_interface.show_message(added_message)
        return True

    # 퀴즈 전체 목록을 화면에 보여줍니다.
    def list_quizzes(self, quiz_catalog: QuizCatalog) -> None:
        console_interface = self.console_interface
        console_interface.show_quiz_list(quiz_catalog)

    # 사용자가 고른 번호의 퀴즈를 삭제합니다.
    def delete_quiz(self, quiz_catalog: QuizCatalog) -> bool:
        console_interface = self.console_interface
        if not quiz_catalog:
            message = constants.MESSAGE_NO_QUIZZES_TO_DELETE
            console_interface.show_message(message)
            return False

        console_interface.show_quiz_list(quiz_catalog)
        delete_prompt = self._delete_prompt(len(quiz_catalog))
        index = console_interface.request_valid_number(
            delete_prompt,
            constants.DISPLAY_INDEX_START,
            len(quiz_catalog),
        )

        delete_confirm_prompt = constants.PROMPT_DELETE_CONFIRM
        if not console_interface.request_yes_no(delete_confirm_prompt):
            cancelled_message = constants.MESSAGE_DELETE_CANCELLED
            console_interface.show_message(cancelled_message)
            return False

        removed_quiz = quiz_catalog.remove_by_display_index(DisplayIndex(index))
        deleted_message = self._deleted_message(removed_quiz)
        console_interface.show_message(deleted_message)
        return True

    def _choices(self, console_interface: ConsoleInterface) -> list[str]:
        return [
            console_interface.request_non_empty_text(self._choice_prompt(index))
            for index in self._choice_indexes()
        ]

    def _choice_indexes(self) -> range:
        start = constants.DISPLAY_INDEX_START
        stop = constants.CHOICE_COUNT + constants.DISPLAY_INDEX_START
        return range(start, stop)

    def _choice_prompt(self, index: int) -> str:
        template = constants.PROMPT_ENTER_CHOICE_TEMPLATE
        return template.format(index=index)

    def _answer_prompt(self) -> str:
        template = constants.PROMPT_ENTER_ANSWER_TEMPLATE
        return template.format(
            min_answer=constants.MIN_ANSWER,
            max_answer=constants.MAX_ANSWER,
        )

    def _delete_prompt(self, quiz_count: int) -> str:
        template = constants.PROMPT_DELETE_INDEX_TEMPLATE
        return template.format(count=quiz_count)

    def _deleted_message(self, removed_quiz: Quiz) -> str:
        payload_item = removed_quiz.payload_item()
        question_field = constants.QUIZ_FIELD_QUESTION
        question = payload_item[question_field]
        template = constants.MESSAGE_DELETE_SUCCESS_TEMPLATE
        return template.format(question=question)
