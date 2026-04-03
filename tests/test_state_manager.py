import tempfile
import unittest
from pathlib import Path

from quiz import Quiz
from state_manager import StateManager


class StateManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.state_file = Path(self.temp_dir.name) / "state.json"
        self.manager = StateManager(self.state_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_validate_quiz_item_accepts_valid_item(self):
        item = {
            "question": "문제",
            "choices": ["A", "B", "C", "D"],
            "answer": 1,
        }

        self.manager._validate_quiz_item(item)

    def test_validate_quiz_item_rejects_invalid_answer(self):
        item = {
            "question": "문제",
            "choices": ["A", "B", "C", "D"],
            "answer": 5,
        }

        with self.assertRaises(ValueError):
            self.manager._validate_quiz_item(item)

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

        self.manager._validate_state_data(data)

    def test_validate_state_data_rejects_missing_quizzes(self):
        data = {"best_score": None}

        with self.assertRaises(ValueError):
            self.manager._validate_state_data(data)

    def test_quiz_to_dict_and_from_dict_are_consistent(self):
        quiz = Quiz("문제", ["A", "B", "C", "D"], 2, hint="힌트")

        item = self.manager._quiz_to_dict(quiz)
        restored = self.manager._quiz_from_dict(item)

        self.assertEqual(restored.question, quiz.question)
        self.assertEqual(restored.choices, quiz.choices)
        self.assertEqual(restored.answer, quiz.answer)
        self.assertEqual(restored.hint, quiz.hint)

    def test_save_and_load_state_round_trip(self):
        quizzes = [Quiz("문제", ["A", "B", "C", "D"], 1, hint="힌트")]

        self.manager.save_state(
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

        state = self.manager.load_state()

        self.assertEqual(len(state["quizzes"]), 1)
        self.assertEqual(state["best_score"], 40)
        self.assertEqual(state["history"][0]["score"], 38)

    def test_load_state_raises_file_not_found(self):
        missing_manager = StateManager(Path(self.temp_dir.name) / "missing.json")

        with self.assertRaises(FileNotFoundError):
            missing_manager.load_state()

    def test_load_state_normalizes_broken_json_to_value_error(self):
        self.state_file.write_text("{broken json", encoding="utf-8")

        with self.assertRaises(ValueError):
            self.manager.load_state()

    def test_validate_history_item_rejects_correct_count_over_total(self):
        item = {
            "played_at": "2026-04-03T15:30:00",
            "total_questions": 3,
            "correct_count": 4,
            "score": 20,
            "hint_used_count": 0,
        }

        with self.assertRaises(ValueError):
            self.manager._validate_history_item(item)

    def test_validate_history_item_rejects_hint_count_over_total(self):
        item = {
            "played_at": "2026-04-03T15:30:00",
            "total_questions": 2,
            "correct_count": 1,
            "score": 8,
            "hint_used_count": 3,
        }

        with self.assertRaises(ValueError):
            self.manager._validate_history_item(item)


if __name__ == "__main__":
    unittest.main()
