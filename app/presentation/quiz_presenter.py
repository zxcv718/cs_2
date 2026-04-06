import app.config.constants as constants
from app.model.quiz import Quiz
from app.service.quiz_metrics import DisplayIndex, QuestionCount


class QuizPresenter:
    def listing_lines(
        self,
        quiz: Quiz,
        display_index: DisplayIndex,
    ) -> tuple[str, ...]:
        listing_template = constants.QUIZ_LIST_ITEM_TEMPLATE
        question_line = self._question_line(quiz)
        listing_header = listing_template.format(
            index=int(display_index),
            question=question_line,
        )
        choice_lines = self._choice_lines(
            quiz,
            constants.QUIZ_LIST_CHOICE_TEMPLATE,
        )
        return (listing_header, *choice_lines)

    def question_lines(
        self,
        quiz: Quiz,
        display_index: DisplayIndex,
        total_questions: QuestionCount,
    ) -> tuple[str, ...]:
        header_template = constants.QUESTION_HEADER_TEMPLATE
        question_line = self._question_line(quiz)
        question_header = header_template.format(
            index=int(display_index),
            total=int(total_questions),
            question=question_line,
        )
        choice_lines = self._choice_lines(
            quiz,
            constants.QUESTION_CHOICE_TEMPLATE,
        )
        return (question_header, *choice_lines)

    def hint_message(self, quiz: Quiz) -> str:
        hint_text = quiz.hint_text()
        if hint_text is None:
            return constants.EMPTY_TEXT
        return hint_text

    def wrong_answer_message(self, quiz: Quiz) -> str:
        answer = quiz.answer_number()
        choice_index = answer - constants.DISPLAY_INDEX_START
        choice_values = quiz.choice_texts()
        correct_text = choice_values[choice_index]
        error_template = constants.ERROR_WRONG_ANSWER_TEMPLATE
        return error_template.format(
            answer=answer,
            correct_text=correct_text,
        )

    def _question_line(self, quiz: Quiz) -> str:
        return quiz.question_text()

    def _choice_lines(
        self,
        quiz: Quiz,
        choice_template: str,
    ) -> tuple[str, ...]:
        choice_values = quiz.choice_texts()
        start = constants.DISPLAY_INDEX_START
        return tuple(
            choice_template.format(
                choice_index=choice_index,
                choice=choice,
            )
            for choice_index, choice in enumerate(choice_values, start=start)
        )
