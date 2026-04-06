from dataclasses import dataclass

from app.service.quiz_metrics import ScoreValue


@dataclass(frozen=True)
class RecordUpdateStatus:
    _updated: bool

    @classmethod
    def updated(cls) -> "RecordUpdateStatus":
        return cls(True)

    @classmethod
    def unchanged(cls) -> "RecordUpdateStatus":
        return cls(False)

    def is_updated(self) -> bool:
        return self._updated


@dataclass(frozen=True)
class BestScore:
    _score_value: ScoreValue | None

    @classmethod
    def empty(cls) -> "BestScore":
        return cls(None)

    @classmethod
    def from_optional_int(cls, score_value: int | None) -> "BestScore":
        if score_value is None:
            return cls.empty()
        return cls(ScoreValue(score_value))

    def to_optional_int(self) -> int | None:
        score_value = self._score_value
        if score_value is None:
            return None
        return int(score_value)

    def update_with(self, score: ScoreValue) -> "BestScoreUpdate":
        if self._score_value is None or score > self._score_value:
            return BestScoreUpdate(BestScore(score), RecordUpdateStatus.updated())
        return BestScoreUpdate(self, RecordUpdateStatus.unchanged())


@dataclass(frozen=True)
class BestScoreUpdate:
    _best_score: BestScore
    _status: RecordUpdateStatus

    def best_score(self) -> BestScore:
        return self._best_score

    def record_status(self) -> RecordUpdateStatus:
        return self._status

    def is_updated(self) -> bool:
        status = self._status
        return status.is_updated()


class BestScoreService:
    def update_best_score(
        self,
        best_score: BestScore,
        score: ScoreValue,
    ) -> BestScoreUpdate:
        return best_score.update_with(score)
