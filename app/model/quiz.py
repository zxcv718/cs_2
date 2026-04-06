import app.config.constants as c
from app.model.quiz_components import QuizPrompt, QuizSolution


# 퀴즈 한 문제의 관련 동작만 표현하는 클래스
class Quiz:
    def __init__(self, prompt: QuizPrompt, solution: QuizSolution) -> None:
        self.prompt = prompt
        self.solution = solution

    def matches(self, user_answer: int) -> bool:
        return self.solution.matches(user_answer)

    def can_offer_hint(self) -> bool:
        return self.solution.can_offer_hint()

    def optional_hint_message(self) -> str | None:
        if not self.can_offer_hint():
            return None
        return self.solution.render_hint_line()

    def payload_item(self) -> dict[str, object]:
        item: dict[str, object] = {
            c.QUIZ_FIELD_QUESTION: self.prompt.render_question_line(),
            c.QUIZ_FIELD_CHOICES: list(self.prompt.render_choice_lines()),
            c.QUIZ_FIELD_ANSWER: self.solution.answer_number.value,
        }
        hint_line = self.optional_hint_message()
        if hint_line is None:
            return item
        item[c.QUIZ_FIELD_HINT] = hint_line
        return item

    def render_listing_lines(self, display_index: int) -> tuple[str, ...]:
        return self.prompt.render_listing_lines(display_index)

    def render_question_lines(
        self,
        display_index: int,
        total_questions: int,
    ) -> tuple[str, ...]:
        return self.prompt.render_question_lines(display_index, total_questions)

    def render_hint_message(self) -> str:
        return self.solution.render_hint_line()

    def render_wrong_answer_message(self) -> str:
        return self.solution.render_wrong_answer_message(self.prompt)
