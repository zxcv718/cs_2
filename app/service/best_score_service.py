from typing import Optional, Tuple

from app.service.quiz_metrics import ScoreValue


# 최고 점수 갱신 규칙만 담당하는 서비스입니다.
class BestScoreService:
    # 최고 점수가 갱신됐는지 함께 알려줍니다.
    def update_best_score(
        self,
        best_score: Optional[ScoreValue],
        score: ScoreValue,
    ) -> Tuple[ScoreValue, bool]:
        if best_score is None or score > best_score:
            return score, True
        return best_score, False
