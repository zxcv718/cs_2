from typing import Any, Optional

import app.config.constants as constants
from app.model.quiz import Quiz
from app.model.quiz_factory import QuizFactory


class DefaultGameStateFactory:
    """
    프로그램 시작 시 사용할 기본 게임 상태를 만들어 주는 팩토리입니다.

    이 클래스는 엄밀한 의미의 Factory Method 패턴보다는
    "객체 생성 책임을 한 곳에 모아 둔 간단한 팩토리"에 가깝습니다.

    이 클래스를 Quiz와 분리한 가장 큰 이유는 단일 책임 원칙(SRP)입니다.
    Quiz는 "퀴즈 한 개의 데이터와 동작"에 집중하고,
    이 팩토리는 "게임 시작 시 필요한 기본 객체와 상태를 조립하는 일"을 맡습니다.
    이렇게 나누면 퀴즈 자체의 변경과 초기화 방식의 변경이 서로 덜 엉키게 됩니다.

    이렇게 분리해 두면 좋은 점:
    1. Quiz 객체와 기본 state를 만드는 규칙을 한 파일에서 관리할 수 있습니다.
    2. 기본값이나 생성 방식이 바뀌어도 이 클래스만 수정하면 됩니다.
    3. 다른 코드는 생성 과정 대신 "완성된 상태를 사용"하는 데 집중할 수 있습니다.
    """

    def __init__(self, quiz_factory: Optional[QuizFactory] = None) -> None:
        self.quiz_factory = quiz_factory or QuizFactory()

    def create_quizzes(self) -> list[Quiz]:
        """
        상수에 들어 있는 기본 퀴즈 데이터를 Quiz 객체 목록으로 변환합니다.

        예를 들어 문제 형식이 바뀌거나 Quiz 생성자 인자가 달라져도
        이 메서드만 수정하면 되므로 유지보수가 쉬워집니다.
        """
        return [self._quiz(item) for item in constants.DEFAULT_QUIZ_DATA]

    def create_state(self) -> dict[str, Any]:
        """
        게임 시작 시 사용할 기본 상태 딕셔너리를 만듭니다.

        기본 상태 구성:
        - quizzes: create_quizzes()로 만든 기본 퀴즈 목록
        - best_score: 아직 최고 점수가 없으므로 None
        - history: 아직 플레이 기록이 없으므로 빈 리스트
        """
        return {
            constants.STATE_KEY_QUIZZES: self.create_quizzes(),
            constants.STATE_KEY_BEST_SCORE: None,
            constants.STATE_KEY_HISTORY: [],
        }

    def _quiz(self, item: dict[str, Any]) -> Quiz:
        quiz_factory = self.quiz_factory
        question = item[constants.QUIZ_FIELD_QUESTION]
        choices = list(item[constants.QUIZ_FIELD_CHOICES])
        answer = item[constants.QUIZ_FIELD_ANSWER]
        hint = item.get(constants.QUIZ_FIELD_HINT)
        return quiz_factory.create(question, choices, answer, hint=hint)
