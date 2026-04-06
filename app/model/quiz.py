from app.model.quiz_components import QuizPrompt, QuizSolution


# 퀴즈 한 문제의 관련 동작만 표현하는 클래스
class Quiz:
    def __init__(self, prompt: QuizPrompt, solution: QuizSolution) -> None:
        self._prompt = prompt
        self._solution = solution

    def matches(self, user_answer: int) -> bool:
        solution = self._solution
        return solution.matches(user_answer)

    def can_offer_hint(self) -> bool:
        solution = self._solution
        return solution.can_offer_hint()

    def question_text(self) -> str:
        prompt = self._prompt
        question_text = prompt.question_text
        return str(question_text)

    def choice_texts(self) -> tuple[str, ...]:
        prompt = self._prompt
        choice_set = prompt.choice_set
        return choice_set.choice_texts()

    def answer_number(self) -> int:
        solution = self._solution
        return int(solution.answer_number)

    def hint_text(self) -> str | None:
        solution = self._solution
        hint_text = solution.hint_text
        if hint_text is None:
            return None
        return str(hint_text)

    def correct_choice_text(self) -> str:
        prompt = self._prompt
        choice_set = prompt.choice_set
        solution = self._solution
        return choice_set.choice_text(solution.answer_number)
