from dataclasses import dataclass
from typing import Optional

import app.config.constants as c
from app.model.quiz import Quiz
from app.ui.console_ui import ConsoleUI


@dataclass(frozen=True)
class QuizQuestionRoundResult:
    correct_count: int
    hint_used_count: int


class QuizQuestionRoundInterrupted(Exception):
    def __init__(self, hint_used_count: int) -> None:
        super().__init__("quiz question round interrupted")
        self.hint_used_count = hint_used_count


@dataclass
class QuizQuestionRoundState:
    used_hint_for_question: bool = False
    hint_used_count: int = c.INITIAL_HINT_USED_COUNT


class QuizQuestionRoundService:
    def __init__(self, console_interface: ConsoleUI) -> None:
        self.console_interface = console_interface

    def play_round(
        self,
        quiz: Quiz,
        index: int,
        total_questions: int,
    ) -> QuizQuestionRoundResult:
        self.console_interface.show_question(quiz, index, total_questions)
        round_state = QuizQuestionRoundState()

        try:
            return self._play_until_finished(quiz, round_state)
        except (KeyboardInterrupt, EOFError) as exc:
            raise QuizQuestionRoundInterrupted(round_state.hint_used_count) from exc

    def _play_until_finished(
        self,
        quiz: Quiz,
        round_state: QuizQuestionRoundState,
    ) -> QuizQuestionRoundResult:
        while True:
            round_result = self._result_for_next_input(quiz, round_state)
            if round_result is None:
                continue
            return round_result

    def _result_for_next_input(
        self,
        quiz: Quiz,
        round_state: QuizQuestionRoundState,
    ) -> Optional[QuizQuestionRoundResult]:
        user_input = self.console_interface.get_answer_or_hint(
            c.PROMPT_ANSWER,
            c.MIN_ANSWER,
            c.MAX_ANSWER,
        )

        if user_input == c.HINT_COMMAND_VALUE:
            return self._result_for_hint_request(quiz, round_state)

        if not isinstance(user_input, int):
            self.console_interface.show_error(c.ERROR_ANSWER_OR_HINT_INPUT)
            return None

        if quiz.matches(user_input):
            return self._correct_result(round_state)

        return self._wrong_result(quiz, round_state)

    def _result_for_hint_request(
        self,
        quiz: Quiz,
        round_state: QuizQuestionRoundState,
    ) -> Optional[QuizQuestionRoundResult]:
        if not quiz.can_offer_hint():
            self.console_interface.show_error(c.ERROR_NO_HINT_FOR_QUESTION)
            return None

        if round_state.used_hint_for_question:
            self.console_interface.show_error(c.ERROR_HINT_ALREADY_USED)
            return None

        self.console_interface.show_message(
            c.MESSAGE_HINT_TEMPLATE.format(hint=quiz.render_hint_message())
        )
        round_state.used_hint_for_question = True
        round_state.hint_used_count += 1
        return None

    def _correct_result(
        self,
        round_state: QuizQuestionRoundState,
    ) -> QuizQuestionRoundResult:
        self.console_interface.show_message(c.MESSAGE_CORRECT_ANSWER)
        return QuizQuestionRoundResult(
            correct_count=c.DISPLAY_INDEX_START,
            hint_used_count=round_state.hint_used_count,
        )

    def _wrong_result(
        self,
        quiz: Quiz,
        round_state: QuizQuestionRoundState,
    ) -> QuizQuestionRoundResult:
        self.console_interface.show_error(quiz.render_wrong_answer_message())
        return QuizQuestionRoundResult(
            correct_count=c.INITIAL_CORRECT_COUNT,
            hint_used_count=round_state.hint_used_count,
        )
