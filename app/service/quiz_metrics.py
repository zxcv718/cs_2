from dataclasses import dataclass
from datetime import datetime

import app.config.constants as constants


def _validate_non_negative(value: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError("metric value must be an integer")
    if value < constants.MINIMUM_SCORE:
        raise ValueError("metric value must not be negative")
    return value


@dataclass(frozen=True, order=True)
class QuestionCount:
    value: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _validate_non_negative(self.value))

    def __int__(self) -> int:
        return self.value

    def __index__(self) -> int:
        return self.value

    def incremented(self) -> "QuestionCount":
        return QuestionCount(self.value + constants.DISPLAY_INDEX_START)


@dataclass(frozen=True, order=True)
class CorrectAnswerCount:
    value: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _validate_non_negative(self.value))

    def __int__(self) -> int:
        return self.value

    def __index__(self) -> int:
        return self.value

    def add(self, correct_answer_count: "CorrectAnswerCount") -> "CorrectAnswerCount":
        return CorrectAnswerCount(self.value + correct_answer_count.value)


@dataclass(frozen=True, order=True)
class HintUsageCount:
    value: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _validate_non_negative(self.value))

    def __int__(self) -> int:
        return self.value

    def __index__(self) -> int:
        return self.value

    def add(self, hint_usage_count: "HintUsageCount") -> "HintUsageCount":
        return HintUsageCount(self.value + hint_usage_count.value)

    def incremented(self) -> "HintUsageCount":
        return HintUsageCount(self.value + constants.DISPLAY_INDEX_START)


@dataclass(frozen=True, order=True)
class ScoreValue:
    value: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _validate_non_negative(self.value))

    def __int__(self) -> int:
        return self.value

    def __index__(self) -> int:
        return self.value


@dataclass(frozen=True, order=True)
class MenuChoice:
    value: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _validate_non_negative(self.value))

    def __int__(self) -> int:
        return self.value

    def matches(self, menu_value: int) -> bool:
        return self.value == menu_value

    def matches_score(self, has_delete: bool) -> bool:
        if has_delete:
            return self.matches(constants.MENU_SCORE)
        return self.matches(constants.MENU_DELETE)


@dataclass(frozen=True, order=True)
class DisplayIndex:
    value: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _validate_non_negative(self.value))
        if self.value < constants.DISPLAY_INDEX_START:
            raise ValueError("display index must start from one")

    def __int__(self) -> int:
        return self.value

    def __index__(self) -> int:
        return self.value

    def to_storage_index(self) -> int:
        return self.value - constants.DISPLAY_INDEX_START


@dataclass(frozen=True, order=True)
class PlayedAt:
    value: str

    @classmethod
    def now(cls) -> "PlayedAt":
        played_at = datetime.now()
        played_at_text = played_at.isoformat(timespec=constants.DATETIME_TIMESPEC)
        return cls(played_at_text)

    @classmethod
    def from_raw(cls, played_at: str) -> "PlayedAt":
        if not isinstance(played_at, str) or not played_at.strip():
            raise ValueError(constants.ERROR_PLAYED_AT_MUST_BE_NON_EMPTY_STRING)
        return cls(played_at)

    def __str__(self) -> str:
        return self.value
