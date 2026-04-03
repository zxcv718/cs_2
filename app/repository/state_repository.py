from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any

import app.config.constants as c
from app.model.quiz import Quiz


class StateRepository:
    def __init__(self, state_file: str | Path) -> None:
        self.state_file = Path(state_file)

    def load_state(self) -> dict[str, Any]:
        try:
            with self.state_file.open(c.FILE_READ_MODE, encoding=c.STATE_ENCODING) as file:
                data = json.load(file)
        except FileNotFoundError:
            raise
        except JSONDecodeError as exc:
            raise ValueError(c.ERROR_INVALID_JSON_STATE) from exc
        except OSError:
            raise

        try:
            self._validate_state_data(data)
        except ValueError as exc:
            raise ValueError(c.ERROR_INVALID_STATE_SCHEMA) from exc

        quizzes = [self._quiz_from_dict(item) for item in data[c.STATE_KEY_QUIZZES]]
        history = list(data.get(c.STATE_KEY_HISTORY, []))
        return {
            c.STATE_KEY_QUIZZES: quizzes,
            c.STATE_KEY_BEST_SCORE: data[c.STATE_KEY_BEST_SCORE],
            c.STATE_KEY_HISTORY: history,
        }

    def save_state(
        self,
        quizzes: list[Quiz],
        best_score: int | None,
        history: list[dict[str, Any]] | None = None,
    ) -> None:
        if best_score is not None and not self._is_int(best_score):
            raise ValueError(c.ERROR_BEST_SCORE_MUST_BE_INTEGER_OR_NONE)

        payload: dict[str, Any] = {
            c.STATE_KEY_QUIZZES: [self._quiz_to_dict(quiz) for quiz in quizzes],
            c.STATE_KEY_BEST_SCORE: best_score,
        }

        if history is not None:
            for item in history:
                self._validate_history_item(item)
            payload[c.STATE_KEY_HISTORY] = list(history)

        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with self.state_file.open(c.FILE_WRITE_MODE, encoding=c.STATE_ENCODING) as file:
            json.dump(
                payload,
                file,
                ensure_ascii=c.STATE_JSON_ENSURE_ASCII,
                indent=c.STATE_JSON_INDENT,
            )

    def _quiz_to_dict(self, quiz: Quiz) -> dict[str, Any]:
        if not isinstance(quiz, Quiz):
            raise ValueError(c.ERROR_QUIZ_MUST_BE_INSTANCE)
        item = {
            c.QUIZ_FIELD_QUESTION: quiz.question,
            c.QUIZ_FIELD_CHOICES: list(quiz.choices),
            c.QUIZ_FIELD_ANSWER: quiz.answer,
        }
        if quiz.has_hint():
            item[c.QUIZ_FIELD_HINT] = quiz.get_hint_text()
        return item

    def _quiz_from_dict(self, item: dict[str, Any]) -> Quiz:
        self._validate_quiz_item(item)
        return Quiz(
            question=item[c.QUIZ_FIELD_QUESTION],
            choices=list(item[c.QUIZ_FIELD_CHOICES]),
            answer=item[c.QUIZ_FIELD_ANSWER],
            hint=item.get(c.QUIZ_FIELD_HINT),
        )

    def _validate_state_data(self, data: dict[str, Any]) -> None:
        if not isinstance(data, dict):
            raise ValueError(c.ERROR_STATE_MUST_BE_DICTIONARY)
        if c.STATE_KEY_QUIZZES not in data or not isinstance(data[c.STATE_KEY_QUIZZES], list):
            raise ValueError(c.ERROR_STATE_MUST_INCLUDE_QUIZZES)
        if c.STATE_KEY_BEST_SCORE not in data:
            raise ValueError(c.ERROR_STATE_MUST_INCLUDE_BEST_SCORE)

        best_score = data[c.STATE_KEY_BEST_SCORE]
        if best_score is not None and not self._is_int(best_score):
            raise ValueError(c.ERROR_BEST_SCORE_MUST_BE_INTEGER_OR_NONE)

        for item in data[c.STATE_KEY_QUIZZES]:
            self._validate_quiz_item(item)

        history = data.get(c.STATE_KEY_HISTORY)
        if history is not None:
            if not isinstance(history, list):
                raise ValueError(c.ERROR_HISTORY_MUST_BE_LIST)
            for item in history:
                self._validate_history_item(item)

    def _validate_quiz_item(self, item: dict[str, Any]) -> None:
        if not isinstance(item, dict):
            raise ValueError(c.ERROR_QUIZ_ITEM_MUST_BE_DICTIONARY)

        question = item.get(c.QUIZ_FIELD_QUESTION)
        if not isinstance(question, str) or not question.strip():
            raise ValueError(c.ERROR_QUESTION_MUST_BE_NON_EMPTY_STRING)

        choices = item.get(c.QUIZ_FIELD_CHOICES)
        if not isinstance(choices, list) or len(choices) != c.CHOICE_COUNT:
            raise ValueError(
                c.ERROR_CHOICES_LENGTH_TEMPLATE.format(choice_count=c.CHOICE_COUNT)
            )
        for choice in choices:
            if not isinstance(choice, str) or not choice.strip():
                raise ValueError(c.ERROR_CHOICE_MUST_BE_NON_EMPTY_STRING)

        answer = item.get(c.QUIZ_FIELD_ANSWER)
        if not self._is_int(answer) or answer < c.MIN_ANSWER or answer > c.MAX_ANSWER:
            raise ValueError(
                c.ERROR_ANSWER_RANGE_TEMPLATE.format(
                    min_answer=c.MIN_ANSWER,
                    max_answer=c.MAX_ANSWER,
                )
            )

        hint = item.get(c.QUIZ_FIELD_HINT)
        if hint is not None and (not isinstance(hint, str) or not hint.strip()):
            raise ValueError(c.ERROR_HINT_MUST_BE_NON_EMPTY_STRING)

    def _validate_history_item(self, item: dict[str, Any]) -> None:
        if not isinstance(item, dict):
            raise ValueError(c.ERROR_HISTORY_ITEM_MUST_BE_DICTIONARY)

        played_at = item.get(c.HISTORY_FIELD_PLAYED_AT)
        if not isinstance(played_at, str) or not played_at.strip():
            raise ValueError(c.ERROR_PLAYED_AT_MUST_BE_NON_EMPTY_STRING)

        for key in (
            c.HISTORY_FIELD_TOTAL_QUESTIONS,
            c.HISTORY_FIELD_CORRECT_COUNT,
            c.HISTORY_FIELD_SCORE,
        ):
            value = item.get(key)
            if not self._is_int(value) or value < c.MINIMUM_SCORE:
                raise ValueError(c.ERROR_NON_NEGATIVE_INTEGER_TEMPLATE.format(key=key))

        total_questions = item[c.HISTORY_FIELD_TOTAL_QUESTIONS]
        correct_count = item[c.HISTORY_FIELD_CORRECT_COUNT]
        if correct_count > total_questions:
            raise ValueError(c.ERROR_CORRECT_COUNT_EXCEEDS_TOTAL)

        hint_used_count = item.get(c.HISTORY_FIELD_HINT_USED_COUNT, c.INITIAL_HINT_USED_COUNT)
        if not self._is_int(hint_used_count) or hint_used_count < c.MINIMUM_SCORE:
            raise ValueError(
                c.ERROR_NON_NEGATIVE_INTEGER_TEMPLATE.format(
                    key=c.HISTORY_FIELD_HINT_USED_COUNT
                )
            )
        if hint_used_count > total_questions:
            raise ValueError(c.ERROR_HINT_USED_COUNT_EXCEEDS_TOTAL)

    def _is_int(self, value: Any) -> bool:
        return isinstance(value, int) and not isinstance(value, bool)
