from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class QuizSessionResult:
    total_questions: int
    correct_count: int
    hint_used_count: int


class QuizSessionInterrupted(Exception):
    def __init__(self, partial_result: Optional[QuizSessionResult] = None) -> None:
        super().__init__("quiz session interrupted")
        self.partial_result = partial_result
