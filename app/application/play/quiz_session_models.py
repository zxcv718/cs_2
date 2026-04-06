from dataclasses import dataclass

from app.service.quiz_metrics import CorrectAnswerCount, HintUsageCount, QuestionCount


@dataclass(frozen=True)
class AnswerTally:
    _correct_count: CorrectAnswerCount
    _hint_used_count: HintUsageCount

    @classmethod
    def empty(cls) -> "AnswerTally":
        return cls(CorrectAnswerCount(0), HintUsageCount(0))

    def add(self, answer_tally: "AnswerTally") -> "AnswerTally":
        return AnswerTally(
            self._correct_count.add(answer_tally.correct_answers()),
            self._hint_used_count.add(answer_tally.hint_usages()),
        )

    def correct_answers(self) -> CorrectAnswerCount:
        return self._correct_count

    def hint_usages(self) -> HintUsageCount:
        return self._hint_used_count


@dataclass(frozen=True)
class QuizPerformance:
    _total_questions: QuestionCount
    _answer_tally: AnswerTally

    def question_count(self) -> QuestionCount:
        return self._total_questions

    def correct_answers(self) -> CorrectAnswerCount:
        answer_tally = self._answer_tally
        return answer_tally.correct_answers()

    def hint_usages(self) -> HintUsageCount:
        answer_tally = self._answer_tally
        return answer_tally.hint_usages()


class QuizSessionInterrupted(Exception):
    def __init__(self, partial_performance: QuizPerformance | None = None) -> None:
        super().__init__("quiz session interrupted")
        self.partial_performance = partial_performance
