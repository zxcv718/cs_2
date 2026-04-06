from typing import Optional, Union

from app.console.input import ConsoleInput
from app.console.output import ConsoleOutput
from app.model.quiz import Quiz
from app.model.quiz_catalog import QuizCatalog
from app.service.quiz_metrics import DeleteMenuAvailability, DisplayIndex, MenuChoice, QuestionCount


class ConsoleReader:
    console_input: ConsoleInput

    def request_menu_choice(self, min_value: int, max_value: int) -> MenuChoice:
        console_input = self.console_input
        return console_input.request_menu_choice(min_value, max_value)

    def request_valid_number(
        self,
        prompt: str,
        min_value: int,
        max_value: int,
    ) -> int:
        console_input = self.console_input
        return console_input.request_valid_number(prompt, min_value, max_value)

    def request_non_empty_text(self, prompt: str) -> str:
        console_input = self.console_input
        return console_input.request_non_empty_text(prompt)

    def request_yes_no(self, prompt: str) -> bool:
        console_input = self.console_input
        return console_input.request_yes_no(prompt)

    def request_answer_or_hint(
        self,
        prompt: str,
        min_value: int,
        max_value: int,
    ) -> Union[int, str]:
        console_input = self.console_input
        return console_input.request_answer_or_hint(prompt, min_value, max_value)


class ConsoleWriter:
    console_output: ConsoleOutput

    def show_menu(self, delete_menu_availability: DeleteMenuAvailability) -> None:
        console_output = self.console_output
        console_output.show_menu(delete_menu_availability)

    def show_message(self, message: str) -> None:
        console_output = self.console_output
        console_output.show_message(message)

    def show_error(self, message: str) -> None:
        console_output = self.console_output
        console_output.show_error(message)

    def show_quiz_list(self, quiz_catalog: QuizCatalog) -> None:
        console_output = self.console_output
        console_output.show_quiz_list(quiz_catalog)

    def display_best_score(self, best_score: Optional[int]) -> None:
        console_output = self.console_output
        console_output.display_best_score(best_score)

    def show_question(
        self,
        quiz: Quiz,
        index: DisplayIndex,
        total: QuestionCount,
    ) -> None:
        console_output = self.console_output
        console_output.show_question(quiz, index, total)

    def show_result(
        self,
        correct_count: int,
        score: int,
        total_questions: int,
        hint_used_count: int,
    ) -> None:
        console_output = self.console_output
        console_output.show_result(
            correct_count,
            score,
            total_questions,
            hint_used_count,
        )


class ConsoleInterface(
    ConsoleReader,
    ConsoleWriter,
):
    def __init__(
        self,
        console_input: ConsoleInput | None = None,
        console_output: ConsoleOutput | None = None,
    ) -> None:
        output = console_output or ConsoleOutput()
        self.console_output = output
        self.console_input = console_input or ConsoleInput(output.show_error)
