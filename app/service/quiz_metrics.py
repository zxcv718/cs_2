from dataclasses import dataclass
from datetime import datetime

import app.config.constants as constants


def _validate_non_negative(value: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError("metric value must be an integer")
    if value < constants.MINIMUM_SCORE:
        raise ValueError("metric value must not be negative")
    return value


@dataclass(order=True)
class QuestionCount:
    value: int

    def __post_init__(self) -> None:
        raw_value = self.value
        self.value = _validate_non_negative(raw_value)

    def __int__(self) -> int:
        return self.value

    def __index__(self) -> int:
        return self.value

    def incremented(self) -> "QuestionCount":
        current_value = self.value
        increment = constants.DISPLAY_INDEX_START
        return QuestionCount(current_value + increment)


@dataclass(order=True)
class CorrectAnswerCount:
    value: int

    def __post_init__(self) -> None:
        raw_value = self.value
        self.value = _validate_non_negative(raw_value)

    def __int__(self) -> int:
        return self.value

    def __index__(self) -> int:
        return self.value

    def add(self, correct_answer_count: "CorrectAnswerCount") -> "CorrectAnswerCount":
        current_value = self.value
        added_value = correct_answer_count.value
        return CorrectAnswerCount(current_value + added_value)


@dataclass(order=True)
class HintUsageCount:
    value: int

    def __post_init__(self) -> None:
        raw_value = self.value
        self.value = _validate_non_negative(raw_value)

    def __int__(self) -> int:
        return self.value

    def __index__(self) -> int:
        return self.value

    def add(self, hint_usage_count: "HintUsageCount") -> "HintUsageCount":
        current_value = self.value
        added_value = hint_usage_count.value
        return HintUsageCount(current_value + added_value)

    def incremented(self) -> "HintUsageCount":
        current_value = self.value
        increment = constants.DISPLAY_INDEX_START
        return HintUsageCount(current_value + increment)


@dataclass(order=True)
class ScoreValue:
    value: int

    def __post_init__(self) -> None:
        raw_value = self.value
        self.value = _validate_non_negative(raw_value)

    def __int__(self) -> int:
        return self.value

    def __index__(self) -> int:
        return self.value


@dataclass(order=True)
class MenuChoice:
    value: int

    def __post_init__(self) -> None:
        raw_value = self.value
        self.value = _validate_non_negative(raw_value)

    def __int__(self) -> int:
        return self.value

    def matches(self, menu_value: int) -> bool:
        return self.value == menu_value

    def matches_score(self, has_delete: bool) -> bool:
        if has_delete:
            menu_score = constants.MENU_SCORE
            return self.matches(menu_score)
        menu_delete = constants.MENU_DELETE
        return self.matches(menu_delete)


@dataclass(order=True)
class DisplayIndex:
    value: int

    def __post_init__(self) -> None:
        raw_value = self.value
        self.value = _validate_non_negative(raw_value)
        display_index_start = constants.DISPLAY_INDEX_START
        if self.value < display_index_start:
            raise ValueError("display index must start from one")

    def __int__(self) -> int:
        return self.value

    def __index__(self) -> int:
        return self.value

    def to_storage_index(self) -> int:
        current_value = self.value
        display_index_start = constants.DISPLAY_INDEX_START
        return current_value - display_index_start


@dataclass(order=True)
class PlayedAt:
    value: str

    @classmethod
    def now(cls) -> "PlayedAt":
        played_at = datetime.now()
        date_time_timespec = constants.DATETIME_TIMESPEC
        played_at_text = played_at.isoformat(timespec=date_time_timespec)
        return cls(played_at_text)

    @classmethod
    def from_raw(cls, played_at: str) -> "PlayedAt":
        if not isinstance(played_at, str) or not played_at.strip():
            raise ValueError(constants.ERROR_PLAYED_AT_MUST_BE_NON_EMPTY_STRING)
        return cls(played_at)

    def __str__(self) -> str:
        return self.value
