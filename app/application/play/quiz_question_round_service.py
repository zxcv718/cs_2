from dataclasses import dataclass, field
from typing import Optional

import app.config.constants as constants
from app.console.interface import ConsoleInterface
from app.model.quiz import Quiz
from app.presentation.quiz_presenter import QuizPresenter
from app.service.quiz_metrics import (
    CorrectAnswerCount,
    DisplayIndex,
    HintUsageCount,
    QuestionCount,
)


@dataclass(frozen=True)
class QuizQuestionRoundResult:
    correct_count: CorrectAnswerCount
    hint_used_count: HintUsageCount


class QuizQuestionRoundInterrupted(Exception):
    def __init__(self, hint_used_count: HintUsageCount) -> None:
        super().__init__("quiz question round interrupted")
        self.hint_used_count = hint_used_count


@dataclass
class QuizQuestionRoundState:
    used_hint_for_question: bool = False
    hint_used_count: HintUsageCount = field(
        default_factory=lambda: HintUsageCount(constants.INITIAL_HINT_USED_COUNT)
    )


class QuizQuestionRoundService:
    def __init__(
        self,
        console_interface: ConsoleInterface,
        quiz_presenter: Optional[QuizPresenter] = None,
    ) -> None:
        self.console_interface = console_interface
        self.quiz_presenter = quiz_presenter or QuizPresenter()

    def play_round(
        self,
        quiz: Quiz,
        index: DisplayIndex,
        total_questions: QuestionCount,
    ) -> QuizQuestionRoundResult:
        console_interface = self.console_interface
        console_interface.show_question(quiz, index, total_questions)
        round_state = QuizQuestionRoundState()

        try:
            while True:
                round_result = self._result_for_next_input(quiz, round_state)
                if round_result is not None:
                    return round_result
        except (KeyboardInterrupt, EOFError) as exc:
            raise QuizQuestionRoundInterrupted(round_state.hint_used_count) from exc

    def _result_for_next_input(
        self,
        quiz: Quiz,
        round_state: QuizQuestionRoundState,
    ) -> Optional[QuizQuestionRoundResult]:
        console_interface = self.console_interface
        user_input = console_interface.request_answer_or_hint(
            constants.PROMPT_ANSWER,
            constants.MIN_ANSWER,
            constants.MAX_ANSWER,
        )

        if user_input == constants.HINT_COMMAND_VALUE:
            return self._result_for_hint_request(quiz, round_state)

        if not isinstance(user_input, int):
            console_interface.show_error(constants.ERROR_ANSWER_OR_HINT_INPUT)
            return None

        if quiz.matches(user_input):
            return self._correct_result(round_state)

        return self._wrong_result(quiz, round_state)

    def _result_for_hint_request(
        self,
        quiz: Quiz,
        round_state: QuizQuestionRoundState,
    ) -> Optional[QuizQuestionRoundResult]:
        console_interface = self.console_interface
        if not quiz.can_offer_hint():
            console_interface.show_error(constants.ERROR_NO_HINT_FOR_QUESTION)
            return None

        if round_state.used_hint_for_question:
            console_interface.show_error(constants.ERROR_HINT_ALREADY_USED)
            return None

        quiz_presenter = self.quiz_presenter
        hint_template = constants.MESSAGE_HINT_TEMPLATE
        hint_message = hint_template.format(
            hint=quiz_presenter.hint_message(quiz)
        )
        console_interface.show_message(hint_message)
        round_state.used_hint_for_question = True
        hint_used_count = round_state.hint_used_count
        round_state.hint_used_count = hint_used_count.incremented()
        return None

    def _correct_result(
        self,
        round_state: QuizQuestionRoundState,
    ) -> QuizQuestionRoundResult:
        console_interface = self.console_interface
        console_interface.show_message(constants.MESSAGE_CORRECT_ANSWER)
        return QuizQuestionRoundResult(
            correct_count=CorrectAnswerCount(constants.DISPLAY_INDEX_START),
            hint_used_count=round_state.hint_used_count,
        )

    def _wrong_result(
        self,
        quiz: Quiz,
        round_state: QuizQuestionRoundState,
    ) -> QuizQuestionRoundResult:
        console_interface = self.console_interface
        quiz_presenter = self.quiz_presenter
        wrong_answer_message = quiz_presenter.wrong_answer_message(quiz)
        console_interface.show_error(wrong_answer_message)
        return QuizQuestionRoundResult(
            correct_count=CorrectAnswerCount(constants.INITIAL_CORRECT_COUNT),
            hint_used_count=round_state.hint_used_count,
        )
