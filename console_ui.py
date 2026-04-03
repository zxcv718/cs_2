from __future__ import annotations

from constants import APP_TITLE, HINT_TOKENS, NO_TOKENS, YES_TOKENS
from quiz import Quiz


class ConsoleUI:
    def show_menu(self, has_delete: bool = False) -> None:
        print("=" * 40)
        print(f"{APP_TITLE:^40}")
        print("=" * 40)
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        if has_delete:
            print("4. 퀴즈 삭제")
            print("5. 점수 확인")
            print("6. 종료")
        else:
            print("4. 점수 확인")
            print("5. 종료")
        print("=" * 40)

    def get_menu_choice(self, min_value: int, max_value: int) -> int:
        return self.get_valid_number("선택: ", min_value, max_value)

    def get_valid_number(self, prompt: str, min_value: int, max_value: int) -> int:
        while True:
            raw = input(prompt)
            normalized = raw.strip()

            if not normalized:
                self.show_error("빈 입력은 허용되지 않습니다.")
                continue

            try:
                value = int(normalized)
            except ValueError:
                self.show_error("숫자를 입력해주세요.")
                continue

            if value < min_value or value > max_value:
                self.show_error(f"{min_value}부터 {max_value} 사이의 숫자를 입력해주세요.")
                continue

            return value

    def get_non_empty_text(self, prompt: str) -> str:
        while True:
            value = input(prompt).strip()
            if not value:
                self.show_error("빈 입력은 허용되지 않습니다.")
                continue
            return value

    def get_yes_no(self, prompt: str) -> bool:
        while True:
            value = input(prompt).strip().lower()
            if value in YES_TOKENS:
                return True
            if value in NO_TOKENS:
                return False
            self.show_error("y/yes 또는 n/no로 입력해주세요.")

    def get_answer_or_hint(self, prompt: str, min_value: int = 1, max_value: int = 4) -> int | str:
        while True:
            value = input(prompt).strip().lower()

            if not value:
                self.show_error("빈 입력은 허용되지 않습니다.")
                continue

            if value in HINT_TOKENS:
                return "hint"

            try:
                number = int(value)
            except ValueError:
                self.show_error("정답 번호 또는 h/hint를 입력해주세요.")
                continue

            if number < min_value or number > max_value:
                self.show_error(f"{min_value}부터 {max_value} 사이의 숫자를 입력해주세요.")
                continue

            return number

    def show_message(self, message: str) -> None:
        print(message)

    def show_error(self, message: str) -> None:
        print(f"[오류] {message}")

    def show_quiz_list(self, quizzes: list[Quiz]) -> None:
        if not quizzes:
            self.show_message("등록된 퀴즈가 없습니다.")
            return

        print("=" * 40)
        print("퀴즈 목록")
        print("=" * 40)
        for index, quiz in enumerate(quizzes, start=1):
            print(f"{index}. {quiz.question}")
            for choice_index, choice in enumerate(quiz.choices, start=1):
                print(f"   {choice_index}) {choice}")
        print("=" * 40)

    def show_best_score(self, best_score: int | None) -> None:
        if best_score is None:
            self.show_message("아직 퀴즈를 시작하지 않았습니다.")
            return
        self.show_message(f"최고 점수: {best_score}점")

    def show_question(self, quiz: Quiz, index: int, total: int) -> None:
        print("-" * 40)
        print(f"[문제 {index}/{total}] {quiz.question}")
        for choice_index, choice in enumerate(quiz.choices, start=1):
            print(f"{choice_index}. {choice}")
        if quiz.has_hint():
            print("힌트를 보려면 h 또는 hint를 입력하세요.")
        print("-" * 40)

    def show_result(
        self,
        correct_count: int,
        score: int,
        total_questions: int,
        hint_used_count: int = 0,
    ) -> None:
        print("=" * 40)
        print("결과")
        print("=" * 40)
        print(f"맞힌 문제 수: {correct_count}/{total_questions}")
        print(f"점수: {score}")
        if hint_used_count:
            print(f"힌트 사용 수: {hint_used_count}")
        print("=" * 40)
