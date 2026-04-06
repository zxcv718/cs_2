from typing import Optional

import app.config.constants as constants
from app.model.quiz import Quiz
from app.model.quiz_catalog import QuizCatalog
from app.presentation.quiz_presenter import QuizPresenter
from app.service.quiz_metrics import DisplayIndex, QuestionCount


class ConsoleOutput:
    def __init__(self, quiz_presenter: QuizPresenter | None = None) -> None:
        self.quiz_presenter = quiz_presenter or QuizPresenter()

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

    def show_message(self, message: str) -> None:
        print(message)

    def show_error(self, message: str) -> None:
        print(f"{constants.ERROR_PREFIX}{message}")

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

    def display_best_score(self, best_score: Optional[int]) -> None:
        show_message = self.show_message
        if best_score is None:
            show_message(constants.MESSAGE_NO_BEST_SCORE)
            return
        template = constants.BEST_SCORE_TEMPLATE
        show_message(template.format(best_score=best_score))

    def show_question(
        self,
        quiz: Quiz,
        index: DisplayIndex,
        total: QuestionCount,
    ) -> None:
        print(constants.SECONDARY_SEPARATOR)
        quiz_presenter = self.quiz_presenter
        question_lines = quiz_presenter.question_lines(quiz, index, total)
        self._print_lines(question_lines)
        self._hint_instruction(quiz)
        print(constants.SECONDARY_SEPARATOR)

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

    def _menu_lines(self, has_delete: bool) -> tuple[str, ...]:
        menu_lines_by_delete = {
            True: constants.MENU_LINES_WITH_DELETE,
            False: constants.MENU_LINES_WITHOUT_DELETE,
        }
        return menu_lines_by_delete[has_delete]

    def _print_lines(self, lines: tuple[str, ...]) -> None:
        for line in lines:
            print(line)

    def _listing_lines(self, quiz_catalog: QuizCatalog) -> None:
        quiz_presenter = self.quiz_presenter
        for raw_index, quiz in enumerate(
            quiz_catalog,
            start=constants.DISPLAY_INDEX_START,
        ):
            display_index = DisplayIndex(raw_index)
            listing_lines = quiz_presenter.listing_lines(
                quiz,
                display_index,
            )
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
