from dataclasses import dataclass
from typing import Optional

from app.service.quiz_metrics import CorrectAnswerCount, HintUsageCount, QuestionCount


@dataclass(frozen=True)
class QuizSessionResult:
    total_questions: QuestionCount
    correct_count: CorrectAnswerCount
    hint_used_count: HintUsageCount


class QuizSessionInterrupted(Exception):
    def __init__(self, partial_result: Optional[QuizSessionResult] = None) -> None:
        super().__init__("quiz session interrupted")
        self.partial_result = partial_result
