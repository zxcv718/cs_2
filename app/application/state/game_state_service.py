from typing import Any, Optional

from app.model.quiz import Quiz
from app.repository.state_repository import StateRepository


# 게임 상태를 불러오고 저장소에 위임하는 서비스입니다.
class GameStateService:
    def __init__(self, state_repository: StateRepository) -> None:
        self.state_repository = state_repository

    # 파일에서 게임 상태를 읽어 반환합니다.
    def load_state(self) -> dict[str, Any]:
        state_repository = self.state_repository
        return state_repository.load_state()

    # 현재 상태를 저장소에 저장합니다.
    def save_state(
        self,
        quizzes: list[Quiz],
        best_score: Optional[int],
        history: list[dict[str, Any]],
    ) -> None:
        state_repository = self.state_repository
        state_repository.save_state(quizzes, best_score, history)
