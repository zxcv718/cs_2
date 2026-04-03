from dataclasses import dataclass

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


class QuizQuestionRoundService:
    def __init__(self, ui: ConsoleUI) -> None:
        self.ui = ui

    def play_round(
        self,
        quiz: Quiz,
        index: int,
        total_questions: int,
    ) -> QuizQuestionRoundResult:
        self.ui.show_question(quiz, index, total_questions)
        used_hint_for_question = False
        hint_used_count = c.INITIAL_HINT_USED_COUNT

        try:
            while True:
                user_input = self.ui.get_answer_or_hint(
                    c.PROMPT_ANSWER,
                    c.MIN_ANSWER,
                    c.MAX_ANSWER,
                )

                if user_input == c.HINT_COMMAND_VALUE:
                    if not quiz.has_hint():
                        self.ui.show_error(c.ERROR_NO_HINT_FOR_QUESTION)
                        continue
                    if used_hint_for_question:
                        self.ui.show_error(c.ERROR_HINT_ALREADY_USED)
                        continue

                    self.ui.show_message(
                        c.MESSAGE_HINT_TEMPLATE.format(hint=quiz.hint_text())
                    )
                    used_hint_for_question = True
                    hint_used_count += 1
                    continue

                if quiz.is_correct(user_input):
                    self.ui.show_message(c.MESSAGE_CORRECT_ANSWER)
                    return QuizQuestionRoundResult(
                        correct_count=c.DISPLAY_INDEX_START,
                        hint_used_count=hint_used_count,
                    )

                self.ui.show_error(
                    c.ERROR_WRONG_ANSWER_TEMPLATE.format(
                        answer=quiz.answer_number(),
                        correct_text=quiz.correct_choice_text(),
                    )
                )
                return QuizQuestionRoundResult(
                    correct_count=c.INITIAL_CORRECT_COUNT,
                    hint_used_count=hint_used_count,
                )
        except (KeyboardInterrupt, EOFError) as exc:
            raise QuizQuestionRoundInterrupted(hint_used_count) from exc
