from app.model.quiz import Quiz
from app.model.quiz_components import (
    ChoiceSet,
    QuizDraft,
    QuizDraftPrompt,
    QuizDraftSolution,
    QuizPrompt,
    QuizSolution,
)


class QuizFactory:
    # Quiz 생성에 필요한 입력 검증과 정규화를 한곳에 모읍니다.
    def create(self, quiz_draft: QuizDraft) -> Quiz:
        prompt = quiz_draft.prompt
        question_text = prompt.question_text
        choice_drafts = prompt.choice_drafts
        choice_set = ChoiceSet.from_drafts(choice_drafts)
        solution = quiz_draft.solution
        answer_number = solution.answer_number
        hint_text = solution.hint_text

        return Quiz(
            QuizPrompt(question_text, choice_set),
            QuizSolution(answer_number, hint_text),
        )
