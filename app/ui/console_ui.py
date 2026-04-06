import app.config.constants as constants
from app.model.quiz import Quiz
from app.model.quiz_catalog import QuizCatalog
from app.service.quiz_metrics import DisplayIndex, MenuChoice, QuestionCount
from typing import Optional, Union


# 콘솔 화면 출력과 사용자 입력을 담당하는 클래스입니다.
class ConsoleUI:
    # 메인 메뉴를 화면에 출력합니다.
    def show_menu(self, has_delete: bool = False) -> None:
        menu_lines = self._menu_lines(has_delete)
        separator = constants.PRIMARY_SEPARATOR
        app_title = constants.APP_TITLE
        separator_length = constants.SEPARATOR_LENGTH
        print(separator)
        print(f"{app_title:^{separator_length}}")
        print(separator)
        for line in menu_lines:
            print(line)
        print(separator)

    # 메뉴 선택 입력을 숫자로 받습니다.
    def request_menu_choice(self, min_value: int, max_value: int) -> MenuChoice:
        return MenuChoice(
            self.request_valid_number(
                constants.PROMPT_MENU_CHOICE,
                min_value,
                max_value,
            )
        )

    # 주어진 범위 안의 숫자가 들어올 때까지 반복해서 입력받습니다.
    def request_valid_number(
        self,
        prompt: str,
        min_value: int,
        max_value: int,
    ) -> int:
        show_error = self.show_error
        while True:
            raw = input(prompt)
            # 앞뒤 공백은 제거하고 검사합니다.
            normalized = raw.strip()

            if not normalized:
                show_error(constants.ERROR_EMPTY_INPUT)
                continue

            try:
                # 문자열 입력을 숫자로 바꿀 수 있어야
                # 이후 범위 검사도 정확하게 할 수 있습니다.
                value = int(normalized)
            except ValueError:
                show_error(constants.ERROR_ENTER_NUMBER)
                continue

            if value < min_value or value > max_value:
                show_error(self._range_error(min_value, max_value))
                continue

            return value

    # 비어 있지 않은 문자열을 받을 때까지 반복합니다.
    def request_non_empty_text(self, prompt: str) -> str:
        show_error = self.show_error
        while True:
            raw_text = input(prompt)
            value = raw_text.strip()
            if not value:
                show_error(constants.ERROR_EMPTY_INPUT)
                continue
            return value

    # y/yes 또는 n/no 입력을 True/False로 바꿉니다.
    def request_yes_no(self, prompt: str) -> bool:
        show_error = self.show_error
        while True:
            raw_text = input(prompt)
            normalized = raw_text.strip()
            value = normalized.lower()
            if value in constants.YES_TOKENS:
                return True
            if value in constants.NO_TOKENS:
                return False
            show_error(constants.ERROR_YES_NO_INPUT)

    # 정답 번호 또는 힌트 명령을 입력받습니다.
    def request_answer_or_hint(
        self,
        prompt: str,
        min_value: int = constants.MIN_ANSWER,
        max_value: int = constants.MAX_ANSWER,
    ) -> Union[int, str]:
        show_error = self.show_error
        while True:
            raw_text = input(prompt)
            normalized = raw_text.strip()
            value = normalized.lower()

            if not value:
                show_error(constants.ERROR_EMPTY_INPUT)
                continue

            # h, hint는 숫자 정답 대신 특별 명령으로 처리합니다.
            if value in constants.HINT_TOKENS:
                return constants.HINT_COMMAND_VALUE

            try:
                number = int(value)
            except ValueError:
                show_error(constants.ERROR_ANSWER_OR_HINT_INPUT)
                continue

            if number < min_value or number > max_value:
                show_error(self._range_error(min_value, max_value))
                continue

            return number

    def _menu_lines(self, has_delete: bool) -> tuple[str, ...]:
        if has_delete:
            return constants.MENU_LINES_WITH_DELETE
        return constants.MENU_LINES_WITHOUT_DELETE

    def _range_error(self, min_value: int, max_value: int) -> str:
        template = constants.ERROR_RANGE_TEMPLATE
        return template.format(
            min_value=min_value,
            max_value=max_value,
        )

    # 일반 안내 문구를 출력합니다.
    def show_message(self, message: str) -> None:
        print(message)

    # 오류 문구 앞에는 공통 접두사를 붙입니다.
    def show_error(self, message: str) -> None:
        print(f"{constants.ERROR_PREFIX}{message}")

    # 저장된 퀴즈 목록을 보기 좋게 출력합니다.
    def show_quiz_list(self, quiz_catalog: QuizCatalog) -> None:
        if not quiz_catalog:
            self.show_message(constants.MESSAGE_NO_QUIZZES)
            return

        separator = constants.PRIMARY_SEPARATOR
        print(separator)
        print(constants.TITLE_QUIZ_LIST)
        print(separator)
        for raw_index, quiz in enumerate(
            quiz_catalog,
            start=constants.DISPLAY_INDEX_START,
        ):
            display_index = DisplayIndex(raw_index)
            for line in quiz.render_listing_lines(display_index):
                print(line)
        print(separator)

    # 최고 점수가 없으면 안내 문구를 보여줍니다.
    def display_best_score(self, best_score: Optional[int]) -> None:
        show_message = self.show_message
        if best_score is None:
            show_message(constants.MESSAGE_NO_BEST_SCORE)
            return
        template = constants.BEST_SCORE_TEMPLATE
        show_message(template.format(best_score=best_score))

    # 현재 출제 중인 문제와 선택지를 출력합니다.
    def show_question(
        self,
        quiz: Quiz,
        index: DisplayIndex,
        total: QuestionCount,
    ) -> None:
        print(constants.SECONDARY_SEPARATOR)
        for line in quiz.render_question_lines(index, total):
            print(line)
        if quiz.can_offer_hint():
            print(constants.MESSAGE_HINT_INSTRUCTION)
        print(constants.SECONDARY_SEPARATOR)

    # 퀴즈가 끝난 뒤 결과를 출력합니다.
    def show_result(
        self,
        correct_count: int,
        score: int,
        total_questions: int,
        hint_used_count: int = constants.INITIAL_HINT_USED_COUNT,
    ) -> None:
        separator = constants.PRIMARY_SEPARATOR
        print(separator)
        print(constants.TITLE_RESULT)
        print(separator)
        print(
            constants.RESULT_CORRECT_TEMPLATE.format(
                correct_count=correct_count,
                total_questions=total_questions,
            )
        )
        print(constants.RESULT_SCORE_TEMPLATE.format(score=score))
        if hint_used_count:
            print(
                constants.RESULT_HINT_USED_TEMPLATE.format(
                    hint_used_count=hint_used_count
                )
            )
        print(separator)
