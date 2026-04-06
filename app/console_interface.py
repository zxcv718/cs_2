import app.config.constants as constants
from app.model.quiz import Quiz
from app.model.quiz_catalog import QuizCatalog
from app.service.quiz_metrics import DisplayIndex, MenuChoice, QuestionCount
from typing import Optional, Union


# 콘솔 화면 출력과 사용자 입력을 담당하는 클래스입니다.
class ConsoleInterface:
    # 메인 메뉴를 화면에 출력합니다.
    def show_menu(self, has_delete: bool = False) -> None:
        menu_lines = self._menu_lines(has_delete)
        separator = constants.PRIMARY_SEPARATOR
        app_title = constants.APP_TITLE
        separator_length = constants.SEPARATOR_LENGTH
        print(separator)
        print(f"{app_title:^{separator_length}}")
        print(separator)
        self._print_lines(menu_lines)
        print(separator)

    # 메뉴 선택 입력을 숫자로 받습니다.
    def request_menu_choice(self, min_value: int, max_value: int) -> MenuChoice:
        prompt = constants.PROMPT_MENU_CHOICE
        menu_number = self.request_valid_number(prompt, min_value, max_value)
        return MenuChoice(menu_number)

    # 주어진 범위 안의 숫자가 들어올 때까지 반복해서 입력받습니다.
    def request_valid_number(
        self,
        prompt: str,
        min_value: int,
        max_value: int,
    ) -> int:
        raw = input(prompt)
        return self._validated_number(raw, prompt, min_value, max_value)

    # 비어 있지 않은 문자열을 받을 때까지 반복합니다.
    def request_non_empty_text(self, prompt: str) -> str:
        raw_text = input(prompt)
        return self._non_empty_text(raw_text, prompt)

    # y/yes 또는 n/no 입력을 True/False로 바꿉니다.
    def request_yes_no(self, prompt: str) -> bool:
        raw_text = input(prompt)
        return self._yes_or_no(raw_text, prompt)

    # 정답 번호 또는 힌트 명령을 입력받습니다.
    def request_answer_or_hint(
        self,
        prompt: str,
        min_value: int = constants.MIN_ANSWER,
        max_value: int = constants.MAX_ANSWER,
    ) -> Union[int, str]:
        raw_text = input(prompt)
        return self._answer_or_hint(raw_text, prompt, min_value, max_value)

    def _menu_lines(self, has_delete: bool) -> tuple[str, ...]:
        menu_lines_by_delete = {
            True: constants.MENU_LINES_WITH_DELETE,
            False: constants.MENU_LINES_WITHOUT_DELETE,
        }
        return menu_lines_by_delete[has_delete]

    def _range_error(self, min_value: int, max_value: int) -> str:
        template = constants.ERROR_RANGE_TEMPLATE
        return template.format(
            min_value=min_value,
            max_value=max_value,
        )

    def _print_lines(self, lines: tuple[str, ...]) -> None:
        for line in lines:
            print(line)

    def _validated_number(
        self,
        raw: str,
        prompt: str,
        min_value: int,
        max_value: int,
    ) -> int:
        show_error = self.show_error
        normalized = raw.strip()
        if not normalized:
            show_error(constants.ERROR_EMPTY_INPUT)
            return self.request_valid_number(prompt, min_value, max_value)
        return self._parsed_number(normalized, prompt, min_value, max_value)

    def _parsed_number(
        self,
        normalized: str,
        prompt: str,
        min_value: int,
        max_value: int,
    ) -> int:
        show_error = self.show_error
        try:
            value = int(normalized)
        except ValueError:
            show_error(constants.ERROR_ENTER_NUMBER)
            return self.request_valid_number(prompt, min_value, max_value)
        return self._number_in_range(value, prompt, min_value, max_value)

    def _number_in_range(
        self,
        value: int,
        prompt: str,
        min_value: int,
        max_value: int,
    ) -> int:
        show_error = self.show_error
        if value < min_value or value > max_value:
            range_error = self._range_error(min_value, max_value)
            show_error(range_error)
            return self.request_valid_number(prompt, min_value, max_value)
        return value

    def _non_empty_text(self, raw_text: str, prompt: str) -> str:
        show_error = self.show_error
        value = raw_text.strip()
        if not value:
            show_error(constants.ERROR_EMPTY_INPUT)
            return self.request_non_empty_text(prompt)
        return value

    def _yes_or_no(self, raw_text: str, prompt: str) -> bool:
        show_error = self.show_error
        normalized = raw_text.strip()
        value = normalized.lower()
        if value in constants.YES_TOKENS:
            return True
        if value in constants.NO_TOKENS:
            return False
        show_error(constants.ERROR_YES_NO_INPUT)
        return self.request_yes_no(prompt)

    def _answer_or_hint(
        self,
        raw_text: str,
        prompt: str,
        min_value: int,
        max_value: int,
    ) -> Union[int, str]:
        show_error = self.show_error
        normalized = raw_text.strip()
        value = normalized.lower()
        if not value:
            show_error(constants.ERROR_EMPTY_INPUT)
            return self.request_answer_or_hint(prompt, min_value, max_value)
        if value in constants.HINT_TOKENS:
            return constants.HINT_COMMAND_VALUE
        return self._answer_number(value, prompt, min_value, max_value)

    def _answer_number(
        self,
        value: str,
        prompt: str,
        min_value: int,
        max_value: int,
    ) -> Union[int, str]:
        show_error = self.show_error
        try:
            number = int(value)
        except ValueError:
            show_error(constants.ERROR_ANSWER_OR_HINT_INPUT)
            return self.request_answer_or_hint(prompt, min_value, max_value)
        return self._answer_in_range(number, prompt, min_value, max_value)

    def _answer_in_range(
        self,
        number: int,
        prompt: str,
        min_value: int,
        max_value: int,
    ) -> Union[int, str]:
        show_error = self.show_error
        if number < min_value or number > max_value:
            range_error = self._range_error(min_value, max_value)
            show_error(range_error)
            return self.request_answer_or_hint(prompt, min_value, max_value)
        return number

    # 일반 안내 문구를 출력합니다.
    def show_message(self, message: str) -> None:
        print(message)

    # 오류 문구 앞에는 공통 접두사를 붙입니다.
    def show_error(self, message: str) -> None:
        print(f"{constants.ERROR_PREFIX}{message}")

    # 저장된 퀴즈 목록을 보기 좋게 출력합니다.
    def show_quiz_list(self, quiz_catalog: QuizCatalog) -> None:
        show_message = self.show_message
        if not quiz_catalog:
            show_message(constants.MESSAGE_NO_QUIZZES)
            return

        separator = constants.PRIMARY_SEPARATOR
        print(separator)
        print(constants.TITLE_QUIZ_LIST)
        print(separator)
        self._listing_lines(quiz_catalog)
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
        question_lines = quiz.render_question_lines(index, total)
        self._print_lines(question_lines)
        self._hint_instruction(quiz)
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
        correct_template = constants.RESULT_CORRECT_TEMPLATE
        print(
            correct_template.format(
                correct_count=correct_count,
                total_questions=total_questions,
            )
        )
        score_template = constants.RESULT_SCORE_TEMPLATE
        print(score_template.format(score=score))
        self._hint_usage(hint_used_count)
        print(separator)

    def _listing_lines(self, quiz_catalog: QuizCatalog) -> None:
        for raw_index, quiz in enumerate(
            quiz_catalog,
            start=constants.DISPLAY_INDEX_START,
        ):
            display_index = DisplayIndex(raw_index)
            listing_lines = quiz.render_listing_lines(display_index)
            self._print_lines(listing_lines)

    def _hint_instruction(self, quiz: Quiz) -> None:
        if not quiz.can_offer_hint():
            return
        print(constants.MESSAGE_HINT_INSTRUCTION)

    def _hint_usage(self, hint_used_count: int) -> None:
        if not hint_used_count:
            return
        hint_template = constants.RESULT_HINT_USED_TEMPLATE
        print(
            hint_template.format(
                hint_used_count=hint_used_count
            )
        )
