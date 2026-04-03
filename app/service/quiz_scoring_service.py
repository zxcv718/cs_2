import app.config.constants as c


# 정답 수와 힌트 사용 수를 바탕으로 점수를 계산합니다.
class QuizScoringService:
    def __init__(
        self,
        hint_penalty: int = c.HINT_PENALTY,
        score_per_correct: int = c.SCORE_PER_CORRECT,
    ) -> None:
        self.hint_penalty = hint_penalty
        self.score_per_correct = score_per_correct

    # 정답 점수와 힌트 감점을 반영해 최종 점수를 계산합니다.
    def calculate_score(self, correct_count: int, hint_used_count: int) -> int:
        score = correct_count * self.score_per_correct - hint_used_count * self.hint_penalty
        # 감점이 커도 음수 점수는 만들지 않도록 0점 아래는 막습니다.
        return max(c.MINIMUM_SCORE, score)
