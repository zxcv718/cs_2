from app.model.quiz_components import QuizPrompt, QuizSolution


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
