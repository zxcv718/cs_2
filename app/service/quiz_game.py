from __future__ import annotations

import random
from datetime import datetime
from typing import Any

import app.config.constants as c
from app.model.quiz import Quiz
from app.repository.state_repository import StateRepository
from app.ui.console_ui import ConsoleUI


class QuizGame:
    def __init__(self, ui: ConsoleUI, state_repository: StateRepository) -> None:
        self.ui = ui
        self.state_repository = state_repository
        self.quizzes: list[Quiz] = []
        self.best_score: int | None = None
        self.history: list[dict[str, Any]] = []
        self.hint_penalty = c.HINT_PENALTY
        self._initialized = False

    def create_default_quizzes(self) -> list[Quiz]:
        return [
            Quiz(
                item[c.QUIZ_FIELD_QUESTION],
                list(item[c.QUIZ_FIELD_CHOICES]),
                item[c.QUIZ_FIELD_ANSWER],
                hint=item.get(c.QUIZ_FIELD_HINT),
            )
            for item in c.DEFAULT_QUIZ_DATA
        ]

    def initialize_state(self) -> None:
        try:
            state = self.state_repository.load_state()
            self.quizzes = state[c.STATE_KEY_QUIZZES]
            self.best_score = state[c.STATE_KEY_BEST_SCORE]
            self.history = state.get(c.STATE_KEY_HISTORY, [])
        except FileNotFoundError:
            self.ui.show_message(c.MESSAGE_STATE_FILE_MISSING)
            self.quizzes = self.create_default_quizzes()
            self.best_score = None
            self.history = []
            self.persist_state()
        except ValueError:
            self.ui.show_error(c.ERROR_STATE_CORRUPTED)
            self.quizzes = self.create_default_quizzes()
            self.best_score = None
            self.history = []
            self.persist_state()
        except OSError:
            self.ui.show_error(c.ERROR_STATE_READ)
            self.quizzes = self.create_default_quizzes()
            self.best_score = None
            self.history = []
        finally:
            self._initialized = True

    def persist_state(self) -> None:
        try:
            self.state_repository.save_state(self.quizzes, self.best_score, self.history)
        except OSError:
            self.ui.show_error(c.ERROR_STATE_SAVE)

    def run(self) -> None:
        if not self._initialized:
            self.initialize_state()

        has_delete = c.ENABLE_DELETE_MENU
        max_choice = c.MENU_MAX_CHOICE_WITH_DELETE if has_delete else c.MENU_MAX_CHOICE_WITHOUT_DELETE

        while True:
            try:
                self.ui.show_menu(has_delete=has_delete)
                choice = self.ui.get_menu_choice(c.MENU_MIN_CHOICE, max_choice)

                if choice == c.MENU_PLAY:
                    self.play_quiz()
                elif choice == c.MENU_ADD:
                    self.add_quiz()
                elif choice == c.MENU_LIST:
                    self.list_quizzes()
                elif has_delete and choice == c.MENU_DELETE:
                    self.delete_quiz()
                elif (has_delete and choice == c.MENU_SCORE) or (not has_delete and choice == c.MENU_DELETE):
                    self.show_best_score()
                elif (has_delete and choice == c.MENU_EXIT) or (not has_delete and choice == c.MENU_SCORE):
                    self.persist_state()
                    self.ui.show_message(c.MESSAGE_PROGRAM_EXIT)
                    break
            except (KeyboardInterrupt, EOFError):
                self.ui.show_message(c.MESSAGE_INTERRUPTED_EXIT)
                self.persist_state()
                break

    def play_quiz(self) -> None:
        if not self.quizzes:
            self.ui.show_message(c.MESSAGE_NO_QUIZZES)
            return

        question_count = self.choose_question_count()
        working_quizzes = list(self.quizzes)
        random.shuffle(working_quizzes)
        selected_quizzes = working_quizzes[:question_count]

        correct_count = c.INITIAL_CORRECT_COUNT
        hint_used_count = c.INITIAL_HINT_USED_COUNT

        for index, quiz in enumerate(selected_quizzes, start=c.DISPLAY_INDEX_START):
            self.ui.show_question(quiz, index, len(selected_quizzes))
            used_hint_for_question = False

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
                        c.MESSAGE_HINT_TEMPLATE.format(hint=quiz.get_hint_text())
                    )
                    used_hint_for_question = True
                    hint_used_count += 1
                    continue

                if quiz.is_correct(user_input):
                    correct_count += 1
                    self.ui.show_message(c.MESSAGE_CORRECT_ANSWER)
                else:
                    correct_text = quiz.choices[quiz.answer - c.DISPLAY_INDEX_START]
                    self.ui.show_error(
                        c.ERROR_WRONG_ANSWER_TEMPLATE.format(
                            answer=quiz.answer,
                            correct_text=correct_text,
                        )
                    )
                break

        score = self.calculate_score(correct_count, hint_used_count)
        is_new_record = self.update_best_score(score)
        self.record_history(
            total_questions=len(selected_quizzes),
            correct_count=correct_count,
            score=score,
            hint_used_count=hint_used_count,
        )
        self.persist_state()
        self.ui.show_result(correct_count, score, len(selected_quizzes), hint_used_count)
        if is_new_record:
            self.ui.show_message(c.MESSAGE_BEST_SCORE_UPDATED)

    def add_quiz(self) -> None:
        question = self.ui.get_non_empty_text(c.PROMPT_ENTER_QUESTION)
        choices = [
            self.ui.get_non_empty_text(c.PROMPT_ENTER_CHOICE_TEMPLATE.format(index=index))
            for index in range(c.DISPLAY_INDEX_START, c.CHOICE_COUNT + c.DISPLAY_INDEX_START)
        ]
        answer = self.ui.get_valid_number(
            c.PROMPT_ENTER_ANSWER_TEMPLATE.format(
                min_answer=c.MIN_ANSWER,
                max_answer=c.MAX_ANSWER,
            ),
            c.MIN_ANSWER,
            c.MAX_ANSWER,
        )

        hint = None
        if self.ui.get_yes_no(c.PROMPT_ADD_HINT_CONFIRM):
            hint = self.ui.get_non_empty_text(c.PROMPT_ENTER_HINT)

        self.quizzes.append(Quiz(question, choices, answer, hint=hint))
        self.persist_state()
        self.ui.show_message(c.MESSAGE_QUIZ_ADDED)

    def list_quizzes(self) -> None:
        self.ui.show_quiz_list(self.quizzes)

    def show_best_score(self) -> None:
        self.ui.show_best_score(self.best_score)

    def update_best_score(self, score: int) -> bool:
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            return True
        return False

    def choose_question_count(self) -> int:
        return self.ui.get_valid_number(
            c.PROMPT_QUESTION_COUNT_TEMPLATE.format(count=len(self.quizzes)),
            c.DISPLAY_INDEX_START,
            len(self.quizzes),
        )

    def calculate_score(self, correct_count: int, hint_used_count: int) -> int:
        score = correct_count * c.SCORE_PER_CORRECT - hint_used_count * self.hint_penalty
        return max(c.MINIMUM_SCORE, score)

    def delete_quiz(self) -> None:
        if not self.quizzes:
            self.ui.show_message(c.MESSAGE_NO_QUIZZES_TO_DELETE)
            return

        self.ui.show_quiz_list(self.quizzes)
        index = self.ui.get_valid_number(
            c.PROMPT_DELETE_INDEX_TEMPLATE.format(count=len(self.quizzes)),
            c.DISPLAY_INDEX_START,
            len(self.quizzes),
        )

        if not self.ui.get_yes_no(c.PROMPT_DELETE_CONFIRM):
            self.ui.show_message(c.MESSAGE_DELETE_CANCELLED)
            return

        removed_quiz = self.quizzes.pop(index - c.DISPLAY_INDEX_START)
        self.persist_state()
        self.ui.show_message(
            c.MESSAGE_DELETE_SUCCESS_TEMPLATE.format(question=removed_quiz.question)
        )

    def record_history(
        self,
        total_questions: int,
        correct_count: int,
        score: int,
        hint_used_count: int = c.INITIAL_HINT_USED_COUNT,
    ) -> None:
        self.history.append(
            {
                c.HISTORY_FIELD_PLAYED_AT: datetime.now().isoformat(
                    timespec=c.DATETIME_TIMESPEC
                ),
                c.HISTORY_FIELD_TOTAL_QUESTIONS: total_questions,
                c.HISTORY_FIELD_CORRECT_COUNT: correct_count,
                c.HISTORY_FIELD_SCORE: score,
                c.HISTORY_FIELD_HINT_USED_COUNT: hint_used_count,
            }
        )
