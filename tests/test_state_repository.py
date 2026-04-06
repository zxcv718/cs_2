import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.repository.quiz_payload_mapper import QuizPayloadMapper
from app.repository.state_payload_mapper import StatePayloadMapper
from app.repository.state_repository import StateRepository
from app.model.quiz_factory import QuizFactory


class StateRepositoryTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.state_file = Path(self.temp_dir.name) / "state.json"
        self.repository = StateRepository(self.state_file)
        self.quiz_mapper = QuizPayloadMapper()
        self.state_mapper = StatePayloadMapper()
        self.quiz_factory = QuizFactory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_quiz_payload_mapper_accepts_valid_item(self):
        item = {
            "question": "문제",
            "choices": ["A", "B", "C", "D"],
            "answer": 1,
        }

        quiz = self.quiz_mapper.from_payload(item)
        payload_item = self.quiz_mapper.to_payload(quiz)

        self.assertEqual(payload_item["question"], "문제")
        self.assertEqual(payload_item["answer"], 1)

    def test_quiz_payload_mapper_rejects_invalid_answer(self):
        item = {
            "question": "문제",
            "choices": ["A", "B", "C", "D"],
            "answer": 5,
        }

        with self.assertRaises(ValueError):
            self.quiz_mapper.from_payload(item)

    def test_state_payload_mapper_accepts_required_schema(self):
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

        state = self.state_mapper.from_payload(data)
        payload = self.state_mapper.to_payload(state)

        self.assertEqual(len(state.quiz_catalog()), 1)
        self.assertIsNone(payload["best_score"])

    def test_state_payload_mapper_rejects_missing_quizzes(self):
        data = {"best_score": None}

        with self.assertRaises(ValueError):
            self.state_mapper.from_payload(data)

    def test_quiz_payload_mapper_round_trip_is_consistent(self):
        quiz = self.quiz_factory.create("문제", ["A", "B", "C", "D"], 2, hint="힌트")

        item = self.quiz_mapper.to_payload(quiz)
        restored = self.quiz_mapper.from_payload(item)
        restored_payload = self.quiz_mapper.to_payload(restored)
        original_payload = self.quiz_mapper.to_payload(quiz)

        self.assertEqual(restored_payload, original_payload)

    def test_save_and_load_state_round_trip(self):
        quizzes = [self.quiz_factory.create("문제", ["A", "B", "C", "D"], 1, hint="힌트")]
        snapshot = self.state_mapper.from_payload(
            {
                "quizzes": [self.quiz_mapper.to_payload(quiz) for quiz in quizzes],
                "best_score": 40,
                "history": [
                    {
                        "played_at": "2026-04-03T15:30:00",
                        "total_questions": 5,
                        "correct_count": 4,
                        "score": 38,
                        "hint_used_count": 1,
                    }
                ],
            }
        )

        self.repository.save_state(snapshot)

        state = self.repository.load_state()
        payload = self.state_mapper.to_payload(state)

        self.assertEqual(len(state.quiz_catalog()), 1)
        self.assertEqual(payload["best_score"], 40)
        self.assertEqual(payload["history"][0]["score"], 38)

    def test_load_state_raises_file_not_found(self):
        missing_repository = StateRepository(Path(self.temp_dir.name) / "missing.json")

        with self.assertRaises(FileNotFoundError):
            missing_repository.load_state()

    def test_load_state_normalizes_broken_json_to_value_error(self):
        self.state_file.write_text("{broken json", encoding="utf-8")

        with self.assertRaises(ValueError):
            self.repository.load_state()

    def test_save_state_preserves_original_file_when_replace_fails(self):
        original_text = '{"status": "original"}'
        self.state_file.write_text(original_text, encoding="utf-8")
        quizzes = [self.quiz_factory.create("문제", ["A", "B", "C", "D"], 1)]
        snapshot = self.state_mapper.from_payload(
            {
                "quizzes": [self.quiz_mapper.to_payload(quiz) for quiz in quizzes],
                "best_score": 10,
                "history": [],
            }
        )

        with patch("pathlib.Path.replace", side_effect=OSError("replace failed")):
            with self.assertRaises(OSError):
                self.repository.save_state(snapshot)

        self.assertEqual(
            self.state_file.read_text(encoding="utf-8"),
            original_text,
        )
        self.assertEqual(
            sorted(path.name for path in Path(self.temp_dir.name).iterdir()),
            ["state.json"],
        )

    def test_backup_state_file_moves_existing_file_to_backup(self):
        broken_text = "{broken json"
        self.state_file.write_text(broken_text, encoding="utf-8")

        backup_file = self.repository.backup_state_file()

        self.assertIsNotNone(backup_file)
        assert backup_file is not None
        self.assertFalse(self.state_file.exists())
        self.assertTrue(backup_file.exists())
        self.assertEqual(
            backup_file.read_text(encoding="utf-8"),
            broken_text,
        )

    def test_state_payload_mapper_rejects_correct_count_over_total(self):
        data = {
            "quizzes": [
                {
                    "question": "문제",
                    "choices": ["A", "B", "C", "D"],
                    "answer": 1,
                }
            ],
            "best_score": None,
            "history": [
                {
                    "played_at": "2026-04-03T15:30:00",
                    "total_questions": 3,
                    "correct_count": 4,
                    "score": 20,
                    "hint_used_count": 0,
                }
            ],
        }

        with self.assertRaises(ValueError):
            self.state_mapper.from_payload(data)

    def test_state_payload_mapper_rejects_hint_count_over_total(self):
        data = {
            "quizzes": [
                {
                    "question": "문제",
                    "choices": ["A", "B", "C", "D"],
                    "answer": 1,
                }
            ],
            "best_score": None,
            "history": [
                {
                    "played_at": "2026-04-03T15:30:00",
                    "total_questions": 2,
                    "correct_count": 1,
                    "score": 8,
                    "hint_used_count": 3,
                }
            ],
        }

        with self.assertRaises(ValueError):
            self.state_mapper.from_payload(data)


if __name__ == "__main__":
    unittest.main()
