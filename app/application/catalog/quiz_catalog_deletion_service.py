import app.config.constants as constants
from app.console.interface import ConsoleInterface
from app.model.quiz_catalog import QuizCatalog
from app.service.quiz_metrics import DisplayIndex


class QuizCatalogDeletionService:
    def __init__(self, console_interface: ConsoleInterface) -> None:
        self.console_interface = console_interface

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

    def _delete_prompt(self, quiz_count: int) -> str:
        template = constants.PROMPT_DELETE_INDEX_TEMPLATE
        return template.format(count=quiz_count)

    def _deleted_message(self, removed_quiz) -> str:
        prompt = removed_quiz.prompt
        question_text = prompt.question_text
        question = question_text.value
        template = constants.MESSAGE_DELETE_SUCCESS_TEMPLATE
        return template.format(question=question)
