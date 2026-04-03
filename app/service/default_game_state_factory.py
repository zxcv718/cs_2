from typing import Any

import app.config.constants as c
from app.model.quiz import Quiz


# 프로그램 시작 시 사용할 기본 상태를 만드는 팩토리입니다.
class DefaultGameStateFactory:
    # 코드에 들어 있는 기본 퀴즈 데이터를 Quiz 객체로 만듭니다.
    def create_quizzes(self) -> list[Quiz]:
        return [
            Quiz(
                item[c.QUIZ_FIELD_QUESTION],
                list(item[c.QUIZ_FIELD_CHOICES]),
                item[c.QUIZ_FIELD_ANSWER],
                hint=item.get(c.QUIZ_FIELD_HINT),
            )
            for item in c.DEFAULT_QUIZ_DATA
        ]

    # 기본 상태는 기본 퀴즈, 최고 점수 없음, 빈 기록으로 구성됩니다.
    def create_state(self) -> dict[str, Any]:
        return {
            c.STATE_KEY_QUIZZES: self.create_quizzes(),
            c.STATE_KEY_BEST_SCORE: None,
            c.STATE_KEY_HISTORY: [],
        }
