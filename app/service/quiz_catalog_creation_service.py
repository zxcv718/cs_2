from typing import Optional

import app.config.constants as constants
from app.console_interface import ConsoleInterface
from app.model.quiz_catalog import QuizCatalog
from app.model.quiz_factory import QuizFactory


class QuizCatalogCreationService:
    def __init__(
        self,
        console_interface: ConsoleInterface,
        quiz_factory: Optional[QuizFactory] = None,
    ) -> None:
        self.console_interface = console_interface
        self.quiz_factory = quiz_factory or QuizFactory()

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
