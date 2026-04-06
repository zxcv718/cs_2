import unittest
from typing import Any, cast

from app.model.quiz import Quiz
from app.model.quiz_components import (
    AnswerNumber,
    ChoiceDrafts,
    HintText,
    QuestionText,
    QuizDraft,
    QuizDraftPrompt,
    QuizDraftSolution,
)
from app.model.quiz_factory import QuizFactory
from app.presentation.quiz_presenter import QuizPresenter
from app.repository.quiz_payload_mapper import QuizPayloadMapper


def create_quiz(
    question: str,
    choices: list[str],
    answer: int,
    hint: str | None = None,
) -> Quiz:
    quiz_draft = QuizDraft(
        prompt=QuizDraftPrompt(
            QuestionText.from_raw(question),
            ChoiceDrafts.from_iterable(choices),
        ),
        solution=QuizDraftSolution(
            AnswerNumber.from_raw(answer),
            HintText.from_raw(hint),
        ),
    )
    return QuizFactory().create(quiz_draft)


class QuizTestCase(unittest.TestCase):
    def setUp(self):
        self.quiz_mapper = QuizPayloadMapper()

    def test_quiz_init_accepts_valid_data(self):
        quiz = create_quiz(
            question="Python의 창시자는?",
            choices=["Guido", "Linus", "Bjarne", "James"],
            answer=1,
            hint="Guido로 시작",
        )
        payload_item = self.quiz_mapper.to_payload_item(quiz)
        prompt = payload_item.prompt
        solution = payload_item.solution

        self.assertEqual(str(prompt.question_text), "Python의 창시자는?")
        self.assertEqual(prompt.choice_drafts.values, ("Guido", "Linus", "Bjarne", "James"))
        self.assertEqual(int(solution.answer_number), 1)
        assert solution.hint_text is not None
        self.assertEqual(str(solution.hint_text), "Guido로 시작")

    def test_quiz_init_rejects_empty_question(self):
        with self.assertRaises(ValueError):
            create_quiz("", ["A", "B", "C", "D"], 1)

    def test_quiz_init_rejects_choices_not_length_4(self):
        with self.assertRaises(ValueError):
            create_quiz("문제", ["A", "B", "C"], 1)

    def test_quiz_init_rejects_answer_out_of_range(self):
        with self.assertRaises(ValueError):
            create_quiz("문제", ["A", "B", "C", "D"], 0)

    def test_quiz_init_rejects_invalid_hint_type(self):
        with self.assertRaises(ValueError):
            quiz_draft = QuizDraft(
                prompt=QuizDraftPrompt(
                    QuestionText.from_raw("문제"),
                    ChoiceDrafts.from_iterable(["A", "B", "C", "D"]),
                ),
                solution=QuizDraftSolution(
                    AnswerNumber.from_raw(1),
                    HintText.from_raw(cast(Any, 123)),
                ),
            )
            QuizFactory().create(quiz_draft)

    def test_is_correct_returns_true_for_correct_answer(self):
        quiz = create_quiz("문제", ["A", "B", "C", "D"], 2)
        self.assertTrue(quiz.matches(2))

    def test_is_correct_returns_false_for_wrong_answer(self):
        quiz = create_quiz("문제", ["A", "B", "C", "D"], 2)
        self.assertFalse(quiz.matches(3))

    def test_has_hint_and_get_hint_text(self):
        quiz = create_quiz("문제", ["A", "B", "C", "D"], 1, hint="힌트")
        quiz_presenter = QuizPresenter()
        self.assertTrue(quiz.can_offer_hint())
        self.assertEqual(quiz_presenter.hint_message(quiz), "힌트")


if __name__ == "__main__":
    unittest.main()
