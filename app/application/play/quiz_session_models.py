from dataclasses import dataclass

from app.service.quiz_metrics import CorrectAnswerCount, HintUsageCount, QuestionCount


@dataclass(frozen=True)
class AnswerTally:
    correct_answers: CorrectAnswerCount
    hint_usages: HintUsageCount

    @classmethod
    def empty(cls) -> "AnswerTally":
        return cls(CorrectAnswerCount(0), HintUsageCount(0))

    def add(self, answer_tally: "AnswerTally") -> "AnswerTally":
        return AnswerTally(
            self.correct_answers.add(answer_tally.correct_answers),
            self.hint_usages.add(answer_tally.hint_usages),
        )


@dataclass(frozen=True)
class QuizPerformance:
    total_questions: QuestionCount
    answer_tally: AnswerTally


class QuizSessionInterrupted(Exception):
    def __init__(self, partial_performance: QuizPerformance | None = None) -> None:
        super().__init__("quiz session interrupted")
        self.partial_performance = partial_performance
