import tempfile
import unittest
from pathlib import Path

from app.model.quiz import Quiz
from app.repository.state_repository import StateRepository


# StateRepository가 저장과 검증을 올바르게 하는지 테스트합니다.
class StateRepositoryTestCase(unittest.TestCase):
    # 테스트마다 임시 state.json 파일을 준비합니다.
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.state_file = Path(self.temp_dir.name) / "state.json"
        self.repository = StateRepository(self.state_file)

    # 테스트가 끝나면 임시 폴더를 정리합니다.
    def tearDown(self):
        self.temp_dir.cleanup()

    # 올바른 퀴즈 형식은 검증을 통과해야 합니다.
    def test_validate_quiz_item_accepts_valid_item(self):
        item = {
            "question": "문제",
            "choices": ["A", "B", "C", "D"],
            "answer": 1,
        }

        self.repository._validate_quiz_item(item)

    # 정답 번호가 잘못되면 오류가 나야 합니다.
    def test_validate_quiz_item_rejects_invalid_answer(self):
        item = {
            "question": "문제",
            "choices": ["A", "B", "C", "D"],
            "answer": 5,
        }

        with self.assertRaises(ValueError):
            self.repository._validate_quiz_item(item)

    # 필수 키가 있는 상태 데이터는 통과해야 합니다.
    def test_validate_state_data_accepts_required_schema(self):
        data = {
            "quizzes": [
                {
                    "question": "문제",
                    "choices": ["A", "B", "C", "D"],
                    "answer": 1,
                }
            ],
            "best_score": None,
        }

        self.repository._validate_state_data(data)

    # quizzes 키가 빠지면 오류가 나야 합니다.
    def test_validate_state_data_rejects_missing_quizzes(self):
        data = {"best_score": None}

        with self.assertRaises(ValueError):
            self.repository._validate_state_data(data)

    # Quiz 객체를 저장용 딕셔너리로 바꿨다가 다시 복원할 수 있어야 합니다.
    def test_quiz_to_dict_and_from_dict_are_consistent(self):
        quiz = Quiz("문제", ["A", "B", "C", "D"], 2, hint="힌트")

        item = self.repository._quiz_to_dict(quiz)
        restored = self.repository._quiz_from_dict(item)

        self.assertEqual(restored.question, quiz.question)
        self.assertEqual(restored.choices, quiz.choices)
        self.assertEqual(restored.answer, quiz.answer)
        self.assertEqual(restored.hint, quiz.hint)

    # 저장한 내용을 다시 읽었을 때 값이 유지되는지 확인합니다.
    def test_save_and_load_state_round_trip(self):
        quizzes = [Quiz("문제", ["A", "B", "C", "D"], 1, hint="힌트")]

        self.repository.save_state(
            quizzes,
            best_score=40,
            history=[
                {
                    "played_at": "2026-04-03T15:30:00",
                    "total_questions": 5,
                    "correct_count": 4,
                    "score": 38,
                    "hint_used_count": 1,
                }
            ],
        )

        state = self.repository.load_state()

        self.assertEqual(len(state["quizzes"]), 1)
        self.assertEqual(state["best_score"], 40)
        self.assertEqual(state["history"][0]["score"], 38)

    # 파일이 없으면 FileNotFoundError가 나와야 합니다.
    def test_load_state_raises_file_not_found(self):
        missing_repository = StateRepository(Path(self.temp_dir.name) / "missing.json")

        with self.assertRaises(FileNotFoundError):
            missing_repository.load_state()

    # JSON 형식이 깨져 있으면 ValueError로 바꿔서 알려줍니다.
    def test_load_state_normalizes_broken_json_to_value_error(self):
        self.state_file.write_text("{broken json", encoding="utf-8")

        with self.assertRaises(ValueError):
            self.repository.load_state()

    # 맞힌 문제 수가 전체 문제 수보다 크면 안 됩니다.
    def test_validate_history_item_rejects_correct_count_over_total(self):
        item = {
            "played_at": "2026-04-03T15:30:00",
            "total_questions": 3,
            "correct_count": 4,
            "score": 20,
            "hint_used_count": 0,
        }

        with self.assertRaises(ValueError):
            self.repository._validate_history_item(item)

    # 힌트 사용 수가 전체 문제 수보다 크면 안 됩니다.
    def test_validate_history_item_rejects_hint_count_over_total(self):
        item = {
            "played_at": "2026-04-03T15:30:00",
            "total_questions": 2,
            "correct_count": 1,
            "score": 8,
            "hint_used_count": 3,
        }

        with self.assertRaises(ValueError):
            self.repository._validate_history_item(item)


if __name__ == "__main__":
    unittest.main()
