from dataclasses import dataclass

from app.service.quiz_metrics import ScoreValue


@dataclass(frozen=True)
class RecordUpdateStatus:
    updated: bool

    @classmethod
    def changed(cls) -> "RecordUpdateStatus":
        return cls(True)

    @classmethod
    def unchanged(cls) -> "RecordUpdateStatus":
        return cls(False)


@dataclass(frozen=True)
class BestScore:
    score_value: ScoreValue | None

    @classmethod
    def empty(cls) -> "BestScore":
        return cls(None)

    @classmethod
    def from_optional_int(cls, score_value: int | None) -> "BestScore":
        if score_value is None:
            return cls.empty()
        return cls(ScoreValue(score_value))

    def update_with(self, score: ScoreValue) -> "BestScoreUpdate":
        current_best_score = self.score_value
        if current_best_score is None or score > current_best_score:
            return BestScoreUpdate(BestScore(score), RecordUpdateStatus.changed())
        return BestScoreUpdate(self, RecordUpdateStatus.unchanged())


@dataclass(frozen=True)
class BestScoreUpdate:
    best_score: BestScore
    record_update_status: RecordUpdateStatus


class BestScoreService:
    def update_best_score(
        self,
        best_score: BestScore,
        score: ScoreValue,
    ) -> BestScoreUpdate:
        return best_score.update_with(score)
