import unittest

from app.model.quiz import Quiz


# Quiz 클래스의 입력 검증과 기본 동작을 테스트합니다.
class QuizTestCase(unittest.TestCase):
    # 정상 입력이면 속성이 그대로 저장되는지 확인합니다.
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

    # 빈 문제 문장은 허용하지 않아야 합니다.
    def test_quiz_init_rejects_empty_question(self):
        with self.assertRaises(ValueError):
            Quiz(
                question="",
                choices=["A", "B", "C", "D"],
                answer=1,
            )

    # 선택지는 반드시 4개여야 합니다.
    def test_quiz_init_rejects_choices_not_length_4(self):
        with self.assertRaises(ValueError):
            Quiz(
                question="문제",
                choices=["A", "B", "C"],
                answer=1,
            )

    # 정답 번호가 범위를 벗어나면 오류가 나야 합니다.
    def test_quiz_init_rejects_answer_out_of_range(self):
        with self.assertRaises(ValueError):
            Quiz(
                question="문제",
                choices=["A", "B", "C", "D"],
                answer=0,
            )

    # 힌트는 문자열만 허용합니다.
    def test_quiz_init_rejects_invalid_hint_type(self):
        with self.assertRaises(ValueError):
            Quiz(
                question="문제",
                choices=["A", "B", "C", "D"],
                answer=1,
                hint=123,
            )

    # 맞는 번호를 넣으면 True가 나와야 합니다.
    def test_is_correct_returns_true_for_correct_answer(self):
        quiz = Quiz("문제", ["A", "B", "C", "D"], 2)
        self.assertTrue(quiz.is_correct(2))

    # 틀린 번호를 넣으면 False가 나와야 합니다.
    def test_is_correct_returns_false_for_wrong_answer(self):
        quiz = Quiz("문제", ["A", "B", "C", "D"], 2)
        self.assertFalse(quiz.is_correct(3))

    # 힌트 존재 여부와 힌트 문구 반환을 확인합니다.
    def test_has_hint_and_get_hint_text(self):
        quiz = Quiz("문제", ["A", "B", "C", "D"], 1, hint="힌트")
        self.assertTrue(quiz.has_hint())
        self.assertEqual(quiz.get_hint_text(), "힌트")


if __name__ == "__main__":
    unittest.main()
