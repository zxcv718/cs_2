from dataclasses import dataclass, field
from typing import Optional

import app.config.constants as constants
from app.console.interface import ConsoleInterface
from app.model.quiz import Quiz
from app.presentation.quiz_presenter import QuizPresenter
from app.application.play.quiz_session_models import AnswerTally
from app.service.quiz_metrics import (
    CorrectAnswerCount,
    DisplayIndex,
    HintUsageCount,
    QuestionCount,
)


class QuizQuestionRoundInterrupted(Exception):
    def __init__(self, hint_used_count: HintUsageCount) -> None:
        super().__init__("quiz question round interrupted")
        self.hint_used_count = hint_used_count


class HintAlreadyUsed(Exception):
    pass


@dataclass(frozen=True)
class HintUseState:
    used: bool

    @classmethod
    def unused(cls) -> "HintUseState":
        return cls(False)

    def consume(self) -> "HintUseState":
        if self.used:
            raise HintAlreadyUsed
        return HintUseState(True)


@dataclass
class QuizQuestionRoundState:
    hint_use_state: HintUseState = field(default_factory=HintUseState.unused)
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
    ) -> AnswerTally:
        console_interface = self.console_interface
        console_interface.show_question(quiz, index, total_questions)
        round_state = QuizQuestionRoundState()
        return self._protected_round_result(quiz, round_state)

    def _protected_round_result(
        self,
        quiz: Quiz,
        round_state: QuizQuestionRoundState,
    ) -> AnswerTally:
        try:
            return self._round_result(quiz, round_state)
        except (KeyboardInterrupt, EOFError) as interrupted_program:
            raise QuizQuestionRoundInterrupted(round_state.hint_used_count) from interrupted_program

    def _round_result(
        self,
        quiz: Quiz,
        round_state: QuizQuestionRoundState,
    ) -> AnswerTally:
        round_result = self._result_for_next_input(quiz, round_state)
        while round_result is None:
            round_result = self._result_for_next_input(quiz, round_state)
        return round_result

    def _result_for_next_input(
        self,
        quiz: Quiz,
        round_state: QuizQuestionRoundState,
    ) -> AnswerTally | None:
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
    ) -> AnswerTally | None:
        hint_request_handler = HintRequestHandler(
            self.console_interface,
            self.quiz_presenter,
        )
        return hint_request_handler.handle(quiz, round_state)

    def _correct_result(
        self,
        round_state: QuizQuestionRoundState,
    ) -> AnswerTally:
        console_interface = self.console_interface
        console_interface.show_message(constants.MESSAGE_CORRECT_ANSWER)
        return AnswerTally(
            CorrectAnswerCount(constants.DISPLAY_INDEX_START),
            round_state.hint_used_count,
        )

    def _wrong_result(
        self,
        quiz: Quiz,
        round_state: QuizQuestionRoundState,
    ) -> AnswerTally:
        console_interface = self.console_interface
        quiz_presenter = self.quiz_presenter
        wrong_answer_message = quiz_presenter.wrong_answer_message(quiz)
        console_interface.show_error(wrong_answer_message)
        return AnswerTally(
            CorrectAnswerCount(constants.INITIAL_CORRECT_COUNT),
            round_state.hint_used_count,
        )


class HintRequestHandler:
    def __init__(
        self,
        console_interface: ConsoleInterface,
        quiz_presenter: QuizPresenter,
    ) -> None:
        self.console_interface = console_interface
        self.quiz_presenter = quiz_presenter

    def handle(
        self,
        quiz: Quiz,
        round_state: QuizQuestionRoundState,
    ) -> AnswerTally | None:
        if not quiz.can_offer_hint():
            self.console_interface.show_error(constants.ERROR_NO_HINT_FOR_QUESTION)
            return None
        try:
            hint_use_state = round_state.hint_use_state
            round_state.hint_use_state = hint_use_state.consume()
        except HintAlreadyUsed:
            self.console_interface.show_error(constants.ERROR_HINT_ALREADY_USED)
            return None
        self._show_hint(quiz)
        hint_used_count = round_state.hint_used_count
        round_state.hint_used_count = hint_used_count.incremented()
        return None

    def _show_hint(self, quiz: Quiz) -> None:
        hint_template = constants.MESSAGE_HINT_TEMPLATE
        hint_message = hint_template.format(
            hint=self.quiz_presenter.hint_message(quiz)
        )
        self.console_interface.show_message(hint_message)
