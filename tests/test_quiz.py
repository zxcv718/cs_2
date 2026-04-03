import unittest

from app.domain.quiz import Quiz


class QuizTestCase(unittest.TestCase):
    def test_quiz_init_accepts_valid_data(self):
        quiz = Quiz(
            question="Python의 창시자는?",
            choices=["Guido", "Linus", "Bjarne", "James"],
            answer=1,
            hint="Guido로 시작",
        )

        self.assertEqual(quiz.question, "Python의 창시자는?")
        self.assertEqual(quiz.choices, ["Guido", "Linus", "Bjarne", "James"])
        self.assertEqual(quiz.answer, 1)
        self.assertEqual(quiz.hint, "Guido로 시작")

    def test_quiz_init_rejects_empty_question(self):
        with self.assertRaises(ValueError):
            Quiz(
                question="",
                choices=["A", "B", "C", "D"],
                answer=1,
            )

    def test_quiz_init_rejects_choices_not_length_4(self):
        with self.assertRaises(ValueError):
            Quiz(
                question="문제",
                choices=["A", "B", "C"],
                answer=1,
            )

    def test_quiz_init_rejects_answer_out_of_range(self):
        with self.assertRaises(ValueError):
            Quiz(
                question="문제",
                choices=["A", "B", "C", "D"],
                answer=0,
            )

    def test_quiz_init_rejects_invalid_hint_type(self):
        with self.assertRaises(ValueError):
            Quiz(
                question="문제",
                choices=["A", "B", "C", "D"],
                answer=1,
                hint=123,
            )

    def test_is_correct_returns_true_for_correct_answer(self):
        quiz = Quiz("문제", ["A", "B", "C", "D"], 2)
        self.assertTrue(quiz.is_correct(2))

    def test_is_correct_returns_false_for_wrong_answer(self):
        quiz = Quiz("문제", ["A", "B", "C", "D"], 2)
        self.assertFalse(quiz.is_correct(3))

    def test_has_hint_and_get_hint_text(self):
        quiz = Quiz("문제", ["A", "B", "C", "D"], 1, hint="힌트")
        self.assertTrue(quiz.has_hint())
        self.assertEqual(quiz.get_hint_text(), "힌트")

    def test_to_display_data_returns_serializable_copy(self):
        quiz = Quiz("문제", ["A", "B", "C", "D"], 1, hint="힌트")

        display_data = quiz.to_display_data()
        display_data["choices"][0] = "수정됨"

        self.assertEqual(display_data["question"], "문제")
        self.assertEqual(display_data["answer"], 1)
        self.assertEqual(display_data["hint"], "힌트")
        self.assertEqual(quiz.choices[0], "A")


if __name__ == "__main__":
    unittest.main()
