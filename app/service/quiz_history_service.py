from typing import Any

import app.config.constants as constants
from app.service.quiz_metrics import PlayedAt, ScoreValue
from app.service.quiz_session_service import QuizSessionResult


# 플레이 결과를 history 저장 형식으로 바꾸는 서비스입니다.
class QuizHistoryService:
    # 플레이 결과를 history에 저장할 딕셔너리로 바꿉니다.
    def create_entry(
        self,
        result: QuizSessionResult,
        score: ScoreValue,
    ) -> dict[str, Any]:
        # played_at을 같이 저장해 두면
        # 나중에 "언제 플레이했는지"를 history에서 확인할 수 있습니다.
        played_at = PlayedAt.now()
        return {
            constants.HISTORY_FIELD_PLAYED_AT: str(played_at),
            constants.HISTORY_FIELD_TOTAL_QUESTIONS: int(result.total_questions),
            constants.HISTORY_FIELD_CORRECT_COUNT: int(result.correct_count),
            constants.HISTORY_FIELD_SCORE: int(score),
            constants.HISTORY_FIELD_HINT_USED_COUNT: int(result.hint_used_count),
        }
