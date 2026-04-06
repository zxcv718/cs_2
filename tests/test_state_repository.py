import tempfile
import unittest
from pathlib import Path
from typing import cast
from unittest.mock import patch

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
from app.repository.quiz_payload_mapper import QuizPayloadMapper
from app.repository.state_payload_mapper import StatePayloadMapper
from app.repository.state_repository import StateRepository


def create_quiz(question: str, choices: list[str], answer: int, hint: str | None = None):
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


class StateRepositoryTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.state_file = Path(self.temp_dir.name) / "state.json"
        self.repository = StateRepository(self.state_file)
        self.quiz_mapper = QuizPayloadMapper()
        self.state_mapper = StatePayloadMapper()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_quiz_payload_mapper_accepts_valid_item(self):
        item = {
            "question": "문제",
            "choices": ["A", "B", "C", "D"],
            "answer": 1,
        }

        payload_item = self.quiz_mapper._payload_item(item)
        quiz = self.quiz_mapper.from_payload_item(payload_item)
        restored_payload = self.quiz_mapper._payload_dictionary(
            self.quiz_mapper.to_payload_item(quiz)
        )
        restored_payload = cast(dict, restored_payload)

        self.assertEqual(restored_payload["question"], "문제")
        self.assertEqual(restored_payload["answer"], 1)

    def test_quiz_payload_mapper_rejects_invalid_answer(self):
        item = {
            "question": "문제",
            "choices": ["A", "B", "C", "D"],
            "answer": 5,
        }

        with self.assertRaises(ValueError):
            self.quiz_mapper._payload_item(item)

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

        state_payload = self.state_mapper._state_payload(data)
        state = self.state_mapper.from_state_payload(state_payload)
        payload = self.state_mapper._payload_dictionary(
            self.state_mapper.to_state_payload(state)
        )
        payload = cast(dict, payload)

        self.assertEqual(len(state.quiz_catalog), 1)
        self.assertIsNone(payload["best_score"])

    def test_state_payload_mapper_rejects_missing_quizzes(self):
        data = {"best_score": None}

        with self.assertRaises(ValueError):
            self.state_mapper._state_payload(data)

    def test_quiz_payload_mapper_round_trip_is_consistent(self):
        quiz = create_quiz("문제", ["A", "B", "C", "D"], 2, hint="힌트")

        payload_item = self.quiz_mapper.to_payload_item(quiz)
        restored = self.quiz_mapper.from_payload_item(payload_item)
        restored_payload = self.quiz_mapper._payload_dictionary(
            self.quiz_mapper.to_payload_item(restored)
        )
        original_payload = self.quiz_mapper._payload_dictionary(payload_item)
        restored_payload = cast(dict, restored_payload)
        original_payload = cast(dict, original_payload)

        self.assertEqual(restored_payload, original_payload)

    def test_save_and_load_state_round_trip(self):
        quiz = create_quiz("문제", ["A", "B", "C", "D"], 1, hint="힌트")
        quiz_payload_item = self.quiz_mapper.to_payload_item(quiz)
        state_payload = self.state_mapper._state_payload(
            {
                "quizzes": [self.quiz_mapper._payload_dictionary(quiz_payload_item)],
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
        snapshot = self.state_mapper.from_state_payload(state_payload)

        self.repository.save_state(snapshot)

        state = self.repository.load_state()
        restored_payload = self.state_mapper._payload_dictionary(
            self.state_mapper.to_state_payload(state)
        )
        restored_payload = cast(dict, restored_payload)

        self.assertEqual(len(state.quiz_catalog), 1)
        self.assertEqual(restored_payload["best_score"], 40)
        self.assertEqual(restored_payload["history"][0]["score"], 38)

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
        quiz = create_quiz("문제", ["A", "B", "C", "D"], 1)
        quiz_payload_item = self.quiz_mapper.to_payload_item(quiz)
        snapshot = self.state_mapper.from_state_payload(
            self.state_mapper._state_payload(
                {
                    "quizzes": [self.quiz_mapper._payload_dictionary(quiz_payload_item)],
                    "best_score": 10,
                    "history": [],
                }
            )
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
            self.state_mapper._state_payload(data)

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
            self.state_mapper._state_payload(data)


if __name__ == "__main__":
    unittest.main()
