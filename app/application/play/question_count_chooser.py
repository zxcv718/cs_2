import app.config.constants as constants
from app.console.interface import ConsoleInterface
from app.service.quiz_metrics import QuestionCount


class QuestionCountChooser:
    def __init__(self, console_interface: ConsoleInterface) -> None:
        self.console_interface = console_interface

    def show_no_quizzes(self) -> None:
        console_interface = self.console_interface
        console_interface.show_message(constants.MESSAGE_NO_QUIZZES)

    def choose_question_count(self, total_questions: QuestionCount) -> QuestionCount:
        console_interface = self.console_interface
        prompt_template = constants.PROMPT_QUESTION_COUNT_TEMPLATE
        prompt = prompt_template.format(count=int(total_questions))
        question_count = console_interface.request_valid_number(
            prompt,
            constants.DISPLAY_INDEX_START,
            int(total_questions),
        )
        return QuestionCount(question_count)
