from __future__ import annotations

import random
from datetime import datetime
from typing import Any

from constants import (
    ENABLE_DELETE_MENU,
    HINT_PENALTY,
    MAX_ANSWER,
    MENU_ADD,
    MENU_DELETE,
    MENU_EXIT,
    MENU_LIST,
    MENU_PLAY,
    MENU_SCORE,
    MIN_ANSWER,
    SCORE_PER_CORRECT,
)
from console_ui import ConsoleUI
from quiz import Quiz
from state_manager import StateManager


class QuizGame:
    def __init__(self, ui: ConsoleUI, state_manager: StateManager) -> None:
        self.ui = ui
        self.state_manager = state_manager
        self.quizzes: list[Quiz] = []
        self.best_score: int | None = None
        self.history: list[dict[str, Any]] = []
        self.hint_penalty = HINT_PENALTY
        self._initialized = False

    def create_default_quizzes(self) -> list[Quiz]:
        return [
            Quiz(
                "Python의 창시자는?",
                ["Guido van Rossum", "Linus Torvalds", "Bjarne Stroustrup", "James Gosling"],
                1,
                hint="이름이 Guido로 시작합니다.",
            ),
            Quiz(
                "리스트를 만드는 기호는?",
                ["()", "[]", "{}", "<>"],
                2,
                hint="대괄호를 사용합니다.",
            ),
            Quiz(
                "함수를 정의할 때 사용하는 키워드는?",
                ["for", "def", "class", "return"],
                2,
                hint="d로 시작하는 키워드입니다.",
            ),
            Quiz(
                "조건 분기에서 사용할 수 있는 키워드는?",
                ["elif", "import", "break", "pass"],
                1,
                hint="if와 else 사이에서 자주 씁니다.",
            ),
            Quiz(
                "반복문에서 즉시 탈출할 때 주로 사용하는 키워드는?",
                ["continue", "return", "break", "yield"],
                3,
                hint="반복을 끊는 의미의 키워드입니다.",
            ),
        ]

    def initialize_state(self) -> None:
        try:
            state = self.state_manager.load_state()
            self.quizzes = state["quizzes"]
            self.best_score = state["best_score"]
            self.history = state.get("history", [])
        except FileNotFoundError:
            self.ui.show_message("저장 파일이 없어 기본 데이터로 시작합니다.")
            self.quizzes = self.create_default_quizzes()
            self.best_score = None
            self.history = []
            self.persist_state()
        except ValueError:
            self.ui.show_error("저장 파일이 손상되어 기본 데이터로 복구합니다.")
            self.quizzes = self.create_default_quizzes()
            self.best_score = None
            self.history = []
            self.persist_state()
        except OSError:
            self.ui.show_error("저장 파일을 읽는 중 오류가 발생해 기본 데이터로 시작합니다.")
            self.quizzes = self.create_default_quizzes()
            self.best_score = None
            self.history = []
        finally:
            self._initialized = True

    def persist_state(self) -> None:
        try:
            self.state_manager.save_state(self.quizzes, self.best_score, self.history)
        except OSError:
            self.ui.show_error("저장 중 오류가 발생했지만 프로그램은 안전하게 계속 진행합니다.")

    def run(self) -> None:
        if not self._initialized:
            self.initialize_state()

        has_delete = ENABLE_DELETE_MENU
        max_choice = MENU_EXIT if has_delete else MENU_SCORE

        while True:
            try:
                self.ui.show_menu(has_delete=has_delete)
                choice = self.ui.get_menu_choice(MENU_PLAY, max_choice)

                if choice == MENU_PLAY:
                    self.play_quiz()
                elif choice == MENU_ADD:
                    self.add_quiz()
                elif choice == MENU_LIST:
                    self.list_quizzes()
                elif has_delete and choice == MENU_DELETE:
                    self.delete_quiz()
                elif (has_delete and choice == MENU_SCORE) or (not has_delete and choice == MENU_DELETE):
                    self.show_best_score()
                elif (has_delete and choice == MENU_EXIT) or (not has_delete and choice == MENU_SCORE):
                    self.persist_state()
                    self.ui.show_message("프로그램을 종료합니다.")
                    break
            except (KeyboardInterrupt, EOFError):
                self.ui.show_message("\n입력이 중단되어 저장 후 안전하게 종료합니다.")
                self.persist_state()
                break

    def play_quiz(self) -> None:
        if not self.quizzes:
            self.ui.show_message("등록된 퀴즈가 없습니다.")
            return

        question_count = self.choose_question_count()
        working_quizzes = list(self.quizzes)
        random.shuffle(working_quizzes)
        selected_quizzes = working_quizzes[:question_count]

        correct_count = 0
        hint_used_count = 0

        for index, quiz in enumerate(selected_quizzes, start=1):
            self.ui.show_question(quiz, index, len(selected_quizzes))
            used_hint_for_question = False

            while True:
                user_input = self.ui.get_answer_or_hint(
                    "정답 번호를 입력하세요: ",
                    MIN_ANSWER,
                    MAX_ANSWER,
                )

                if user_input == "hint":
                    if not quiz.has_hint():
                        self.ui.show_error("이 문제에는 힌트가 없습니다.")
                        continue
                    if used_hint_for_question:
                        self.ui.show_error("이 문제의 힌트는 이미 사용했습니다.")
                        continue

                    self.ui.show_message(f"힌트: {quiz.get_hint_text()}")
                    used_hint_for_question = True
                    hint_used_count += 1
                    continue

                if quiz.is_correct(user_input):
                    correct_count += 1
                    self.ui.show_message("정답입니다.")
                else:
                    correct_text = quiz.choices[quiz.answer - 1]
                    self.ui.show_error(
                        f"오답입니다. 정답은 {quiz.answer}번 ({correct_text})입니다."
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
            self.ui.show_message("최고 점수가 갱신되었습니다.")

    def add_quiz(self) -> None:
        question = self.ui.get_non_empty_text("문제를 입력하세요: ")
        choices = [
            self.ui.get_non_empty_text(f"선택지 {index}번을 입력하세요: ")
            for index in range(1, 5)
        ]
        answer = self.ui.get_valid_number("정답 번호를 입력하세요(1-4): ", MIN_ANSWER, MAX_ANSWER)

        hint = None
        if self.ui.get_yes_no("힌트를 추가하시겠습니까? (y/n): "):
            hint = self.ui.get_non_empty_text("힌트를 입력하세요: ")

        self.quizzes.append(Quiz(question, choices, answer, hint=hint))
        self.persist_state()
        self.ui.show_message("퀴즈가 추가되었습니다.")

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
            f"몇 문제를 풀겠습니까? (1-{len(self.quizzes)}): ",
            1,
            len(self.quizzes),
        )

    def calculate_score(self, correct_count: int, hint_used_count: int) -> int:
        score = correct_count * SCORE_PER_CORRECT - hint_used_count * self.hint_penalty
        return max(0, score)

    def delete_quiz(self) -> None:
        if not self.quizzes:
            self.ui.show_message("삭제할 퀴즈가 없습니다.")
            return

        self.ui.show_quiz_list(self.quizzes)
        index = self.ui.get_valid_number(
            f"삭제할 퀴즈 번호를 입력하세요 (1-{len(self.quizzes)}): ",
            1,
            len(self.quizzes),
        )

        if not self.ui.get_yes_no("정말 삭제하시겠습니까? (y/n): "):
            self.ui.show_message("삭제를 취소했습니다.")
            return

        removed_quiz = self.quizzes.pop(index - 1)
        self.persist_state()
        self.ui.show_message(f"'{removed_quiz.question}' 퀴즈를 삭제했습니다.")

    def record_history(
        self,
        total_questions: int,
        correct_count: int,
        score: int,
        hint_used_count: int = 0,
    ) -> None:
        self.history.append(
            {
                "played_at": datetime.now().isoformat(timespec="seconds"),
                "total_questions": total_questions,
                "correct_count": correct_count,
                "score": score,
                "hint_used_count": hint_used_count,
            }
        )
