import app.config.constants as constants
from app.application.play.quiz_session_models import AnswerTally, QuizPerformance
from app.service.quiz_metrics import QuestionCount


class QuizPartialResultBuilder:
    def build_performance(
        self,
        total_questions: QuestionCount,
        answer_tally: AnswerTally,
    ) -> QuizPerformance:
        return QuizPerformance(
            total_questions,
            answer_tally,
        )

    def build_interrupted_result(
        self,
        total_questions: QuestionCount,
        answer_tally: AnswerTally,
        answered_question_count: QuestionCount,
    ) -> QuizPerformance | None:
        if int(answered_question_count) < constants.DISPLAY_INDEX_START:
            return None

        return self.build_performance(
            total_questions,
            answer_tally,
        )
