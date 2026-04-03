import app.config.constants as c
from app.model.quiz import Quiz
from typing import Optional, Union


# 콘솔 화면 출력과 사용자 입력을 담당하는 클래스입니다.
class ConsoleUI:
    # 메인 메뉴를 화면에 출력합니다.
    def show_menu(self, has_delete: bool = False) -> None:
        menu_lines = c.MENU_LINES_WITH_DELETE if has_delete else c.MENU_LINES_WITHOUT_DELETE
        print(c.PRIMARY_SEPARATOR)
        print(f"{c.APP_TITLE:^{c.SEPARATOR_LENGTH}}")
        print(c.PRIMARY_SEPARATOR)
        for line in menu_lines:
            print(line)
        print(c.PRIMARY_SEPARATOR)

    # 메뉴 선택 입력을 숫자로 받습니다.
    def get_menu_choice(self, min_value: int, max_value: int) -> int:
        return self.get_valid_number(c.PROMPT_MENU_CHOICE, min_value, max_value)

    # 주어진 범위 안의 숫자가 들어올 때까지 반복해서 입력받습니다.
    def get_valid_number(self, prompt: str, min_value: int, max_value: int) -> int:
        while True:
            raw = input(prompt)
            # 앞뒤 공백은 제거하고 검사합니다.
            normalized = raw.strip()

            if not normalized:
                self.show_error(c.ERROR_EMPTY_INPUT)
                continue

            try:
                # 문자열 입력을 숫자로 바꿀 수 있어야
                # 이후 범위 검사도 정확하게 할 수 있습니다.
                value = int(normalized)
            except ValueError:
                self.show_error(c.ERROR_ENTER_NUMBER)
                continue

            if value < min_value or value > max_value:
                self.show_error(
                    c.ERROR_RANGE_TEMPLATE.format(
                        min_value=min_value,
                        max_value=max_value,
                    )
                )
                continue

            return value

    # 비어 있지 않은 문자열을 받을 때까지 반복합니다.
    def get_non_empty_text(self, prompt: str) -> str:
        while True:
            value = input(prompt).strip()
            if not value:
                self.show_error(c.ERROR_EMPTY_INPUT)
                continue
            return value

    # y/yes 또는 n/no 입력을 True/False로 바꿉니다.
    def get_yes_no(self, prompt: str) -> bool:
        while True:
            value = input(prompt).strip().lower()
            if value in c.YES_TOKENS:
                return True
            if value in c.NO_TOKENS:
                return False
            self.show_error(c.ERROR_YES_NO_INPUT)

    # 정답 번호 또는 힌트 명령을 입력받습니다.
    def get_answer_or_hint(
        self,
        prompt: str,
        min_value: int = c.MIN_ANSWER,
        max_value: int = c.MAX_ANSWER,
    ) -> Union[int, str]:
        while True:
            value = input(prompt).strip().lower()

            if not value:
                self.show_error(c.ERROR_EMPTY_INPUT)
                continue

            # h, hint는 숫자 정답 대신 특별 명령으로 처리합니다.
            if value in c.HINT_TOKENS:
                return c.HINT_COMMAND_VALUE

            try:
                number = int(value)
            except ValueError:
                self.show_error(c.ERROR_ANSWER_OR_HINT_INPUT)
                continue

            if number < min_value or number > max_value:
                self.show_error(
                    c.ERROR_RANGE_TEMPLATE.format(
                        min_value=min_value,
                        max_value=max_value,
                    )
                )
                continue

            return number

    # 일반 안내 문구를 출력합니다.
    def show_message(self, message: str) -> None:
        print(message)

    # 오류 문구 앞에는 공통 접두사를 붙입니다.
    def show_error(self, message: str) -> None:
        print(f"{c.ERROR_PREFIX}{message}")

    # 저장된 퀴즈 목록을 보기 좋게 출력합니다.
    def show_quiz_list(self, quizzes: list[Quiz]) -> None:
        if not quizzes:
            self.show_message(c.MESSAGE_NO_QUIZZES)
            return

        print(c.PRIMARY_SEPARATOR)
        print(c.TITLE_QUIZ_LIST)
        print(c.PRIMARY_SEPARATOR)
        for index, quiz in enumerate(quizzes, start=c.DISPLAY_INDEX_START):
            print(
                c.QUIZ_LIST_ITEM_TEMPLATE.format(
                    index=index,
                    question=quiz.question_text(),
                )
            )
            for choice_index, choice in enumerate(
                quiz.choice_texts(),
                start=c.DISPLAY_INDEX_START,
            ):
                print(
                    c.QUIZ_LIST_CHOICE_TEMPLATE.format(
                        choice_index=choice_index,
                        choice=choice,
                    )
                )
        print(c.PRIMARY_SEPARATOR)

    # 최고 점수가 없으면 안내 문구를 보여줍니다.
    def show_best_score(self, best_score: Optional[int]) -> None:
        if best_score is None:
            self.show_message(c.MESSAGE_NO_BEST_SCORE)
            return
        self.show_message(c.BEST_SCORE_TEMPLATE.format(best_score=best_score))

    # 현재 출제 중인 문제와 선택지를 출력합니다.
    def show_question(self, quiz: Quiz, index: int, total: int) -> None:
        print(c.SECONDARY_SEPARATOR)
        print(
            c.QUESTION_HEADER_TEMPLATE.format(
                index=index,
                total=total,
                question=quiz.question_text(),
            )
        )
        for choice_index, choice in enumerate(
            quiz.choice_texts(),
            start=c.DISPLAY_INDEX_START,
        ):
            print(
                c.QUESTION_CHOICE_TEMPLATE.format(
                    choice_index=choice_index,
                    choice=choice,
                )
            )
        if quiz.has_hint():
            print(c.MESSAGE_HINT_INSTRUCTION)
        print(c.SECONDARY_SEPARATOR)

    # 퀴즈가 끝난 뒤 결과를 출력합니다.
    def show_result(
        self,
        correct_count: int,
        score: int,
        total_questions: int,
        hint_used_count: int = c.INITIAL_HINT_USED_COUNT,
    ) -> None:
        print(c.PRIMARY_SEPARATOR)
        print(c.TITLE_RESULT)
        print(c.PRIMARY_SEPARATOR)
        print(
            c.RESULT_CORRECT_TEMPLATE.format(
                correct_count=correct_count,
                total_questions=total_questions,
            )
        )
        print(c.RESULT_SCORE_TEMPLATE.format(score=score))
        if hint_used_count:
            print(c.RESULT_HINT_USED_TEMPLATE.format(hint_used_count=hint_used_count))
        print(c.PRIMARY_SEPARATOR)
