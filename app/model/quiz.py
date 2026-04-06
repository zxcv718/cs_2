import app.config.constants as constants
from app.model.quiz_components import QuizPrompt, QuizSolution
from app.service.quiz_metrics import DisplayIndex, QuestionCount


# 퀴즈 한 문제의 관련 동작만 표현하는 클래스
class Quiz:
    def __init__(self, prompt: QuizPrompt, solution: QuizSolution) -> None:
        self.prompt = prompt
        self.solution = solution

    def matches(self, user_answer: int) -> bool:
        solution = self.solution
        return solution.matches(user_answer)

    def can_offer_hint(self) -> bool:
        solution = self.solution
        return solution.can_offer_hint()

    def optional_hint_message(self) -> str | None:
        if not self.can_offer_hint():
            return None
        solution = self.solution
        return solution.render_hint_line()

    def payload_item(self) -> dict[str, object]:
        prompt = self.prompt
        solution = self.solution
        item: dict[str, object] = {
            constants.QUIZ_FIELD_QUESTION: prompt.render_question_line(),
            constants.QUIZ_FIELD_CHOICES: list(prompt.render_choice_lines()),
            constants.QUIZ_FIELD_ANSWER: int(solution.answer_number),
        }
        hint_line = self.optional_hint_message()
        if hint_line is None:
            return item
        item[constants.QUIZ_FIELD_HINT] = hint_line
        return item

    def render_listing_lines(self, display_index: DisplayIndex) -> tuple[str, ...]:
        prompt = self.prompt
        return prompt.render_listing_lines(display_index)

    def render_question_lines(
        self,
        display_index: DisplayIndex,
        total_questions: QuestionCount,
    ) -> tuple[str, ...]:
        prompt = self.prompt
        return prompt.render_question_lines(display_index, total_questions)

    def render_hint_message(self) -> str:
        solution = self.solution
        return solution.render_hint_line()

    def render_wrong_answer_message(self) -> str:
        prompt = self.prompt
        solution = self.solution
        return solution.render_wrong_answer_message(prompt)
