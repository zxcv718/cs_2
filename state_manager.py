from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from constants import CHOICE_COUNT, MAX_ANSWER, MIN_ANSWER, STATE_ENCODING
from quiz import Quiz


class StateManager:
    def __init__(self, state_file: str | Path) -> None:
        self.state_file = Path(state_file)

    def load_state(self) -> dict[str, Any]:
        try:
            with self.state_file.open("r", encoding=STATE_ENCODING) as file:
                data = json.load(file)
        except FileNotFoundError:
            raise
        except JSONDecodeError as exc:
            raise ValueError("Invalid JSON state file") from exc
        except OSError:
            raise

        try:
            self._validate_state_data(data)
        except ValueError as exc:
            raise ValueError("Invalid state schema") from exc

        quizzes = [self._quiz_from_dict(item) for item in data["quizzes"]]
        history = list(data.get("history", []))
        return {
            "quizzes": quizzes,
            "best_score": data["best_score"],
            "history": history,
        }

    def save_state(
        self,
        quizzes: list[Quiz],
        best_score: int | None,
        history: list[dict[str, Any]] | None = None,
    ) -> None:
        if best_score is not None and not self._is_int(best_score):
            raise ValueError("best_score must be an integer or None")

        payload: dict[str, Any] = {
            "quizzes": [self._quiz_to_dict(quiz) for quiz in quizzes],
            "best_score": best_score,
        }

        if history is not None:
            for item in history:
                self._validate_history_item(item)
            payload["history"] = list(history)

        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with self.state_file.open("w", encoding=STATE_ENCODING) as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)

    def _quiz_to_dict(self, quiz: Quiz) -> dict[str, Any]:
        if not isinstance(quiz, Quiz):
            raise ValueError("quiz must be a Quiz instance")
        item = {
            "question": quiz.question,
            "choices": list(quiz.choices),
            "answer": quiz.answer,
        }
        if quiz.has_hint():
            item["hint"] = quiz.get_hint_text()
        return item

    def _quiz_from_dict(self, item: dict[str, Any]) -> Quiz:
        self._validate_quiz_item(item)
        return Quiz(
            question=item["question"],
            choices=list(item["choices"]),
            answer=item["answer"],
            hint=item.get("hint"),
        )

    def _validate_state_data(self, data: dict[str, Any]) -> None:
        if not isinstance(data, dict):
            raise ValueError("state must be a dictionary")
        if "quizzes" not in data or not isinstance(data["quizzes"], list):
            raise ValueError("state must include quizzes list")
        if "best_score" not in data:
            raise ValueError("state must include best_score")

        best_score = data["best_score"]
        if best_score is not None and not self._is_int(best_score):
            raise ValueError("best_score must be an integer or None")

        for item in data["quizzes"]:
            self._validate_quiz_item(item)

        history = data.get("history")
        if history is not None:
            if not isinstance(history, list):
                raise ValueError("history must be a list")
            for item in history:
                self._validate_history_item(item)

    def _validate_quiz_item(self, item: dict[str, Any]) -> None:
        if not isinstance(item, dict):
            raise ValueError("quiz item must be a dictionary")

        question = item.get("question")
        if not isinstance(question, str) or not question.strip():
            raise ValueError("question must be a non-empty string")

        choices = item.get("choices")
        if not isinstance(choices, list) or len(choices) != CHOICE_COUNT:
            raise ValueError(f"choices must be a list of {CHOICE_COUNT} items")
        for choice in choices:
            if not isinstance(choice, str) or not choice.strip():
                raise ValueError("choice must be a non-empty string")

        answer = item.get("answer")
        if not self._is_int(answer) or answer < MIN_ANSWER or answer > MAX_ANSWER:
            raise ValueError(f"answer must be between {MIN_ANSWER} and {MAX_ANSWER}")

        hint = item.get("hint")
        if hint is not None and (not isinstance(hint, str) or not hint.strip()):
            raise ValueError("hint must be a non-empty string if provided")

    def _validate_history_item(self, item: dict[str, Any]) -> None:
        if not isinstance(item, dict):
            raise ValueError("history item must be a dictionary")

        played_at = item.get("played_at")
        if not isinstance(played_at, str) or not played_at.strip():
            raise ValueError("played_at must be a non-empty string")

        for key in ("total_questions", "correct_count", "score"):
            value = item.get(key)
            if not self._is_int(value) or value < 0:
                raise ValueError(f"{key} must be a non-negative integer")

        hint_used_count = item.get("hint_used_count", 0)
        if not self._is_int(hint_used_count) or hint_used_count < 0:
            raise ValueError("hint_used_count must be a non-negative integer")

    def _is_int(self, value: Any) -> bool:
        return isinstance(value, int) and not isinstance(value, bool)

