import unittest
from typing import Any, cast

from app.model.quiz import Quiz
from app.model.quiz_factory import QuizFactory
from app.presentation.quiz_presenter import QuizPresenter
from app.repository.quiz_payload_mapper import QuizPayloadMapper


# Quiz 클래스의 입력 검증과 기본 동작을 테스트합니다.
class QuizTestCase(unittest.TestCase):
    def setUp(self):
        self.factory = QuizFactory()

    # 정상 입력이면 속성이 그대로 저장되는지 확인합니다.
    def test_quiz_init_accepts_valid_data(self):
        quiz = self.factory.create(
            question="Python의 창시자는?",
            choices=["Guido", "Linus", "Bjarne", "James"],
            answer=1,
            hint="Guido로 시작",
        )
        payload_item = QuizPayloadMapper().to_payload(quiz)

        self.assertEqual(payload_item["question"], "Python의 창시자는?")
        self.assertEqual(payload_item["choices"], ["Guido", "Linus", "Bjarne", "James"])
        self.assertEqual(payload_item["answer"], 1)
        self.assertEqual(payload_item["hint"], "Guido로 시작")

    # 빈 문제 문장은 허용하지 않아야 합니다.
    def test_quiz_init_rejects_empty_question(self):
        with self.assertRaises(ValueError):
            self.factory.create(
                question="",
                choices=["A", "B", "C", "D"],
                answer=1,
            )

    # 선택지는 반드시 4개여야 합니다.
    def test_quiz_init_rejects_choices_not_length_4(self):
        with self.assertRaises(ValueError):
            self.factory.create(
                question="문제",
                choices=["A", "B", "C"],
                answer=1,
            )

    # 정답 번호가 범위를 벗어나면 오류가 나야 합니다.
    def test_quiz_init_rejects_answer_out_of_range(self):
        with self.assertRaises(ValueError):
            self.factory.create(
                question="문제",
                choices=["A", "B", "C", "D"],
                answer=0,
            )

    # 힌트는 문자열만 허용합니다.
    def test_quiz_init_rejects_invalid_hint_type(self):
        with self.assertRaises(ValueError):
            self.factory.create(
                question="문제",
                choices=["A", "B", "C", "D"],
                answer=1,
                hint=cast(Any, 123),
            )

    # 맞는 번호를 넣으면 True가 나와야 합니다.
    def test_is_correct_returns_true_for_correct_answer(self):
        quiz = self.factory.create("문제", ["A", "B", "C", "D"], 2)
        self.assertTrue(quiz.matches(2))

    # 틀린 번호를 넣으면 False가 나와야 합니다.
    def test_is_correct_returns_false_for_wrong_answer(self):
        quiz = self.factory.create("문제", ["A", "B", "C", "D"], 2)
        self.assertFalse(quiz.matches(3))

    # 힌트 존재 여부와 힌트 문구 반환을 확인합니다.
    def test_has_hint_and_get_hint_text(self):
        quiz = self.factory.create("문제", ["A", "B", "C", "D"], 1, hint="힌트")
        quiz_presenter = QuizPresenter()
        self.assertTrue(quiz.can_offer_hint())
        self.assertEqual(quiz_presenter.hint_message(quiz), "힌트")


if __name__ == "__main__":
    unittest.main()
