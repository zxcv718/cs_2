from pathlib import Path
from app.application.state.game_snapshot import GameSnapshot
from app.repository.state_repository import StateRepository


# 게임 상태를 불러오고 저장소에 위임하는 서비스입니다.
class GameStateService:
    def __init__(self, state_repository: StateRepository) -> None:
        self.state_repository = state_repository

    # 파일에서 게임 상태를 읽어 반환합니다.
    def load_state(self) -> GameSnapshot:
        state_repository = self.state_repository
        return state_repository.load_state()

    # 현재 상태를 저장소에 저장합니다.
    def save_state(self, game_snapshot: GameSnapshot) -> None:
        state_repository = self.state_repository
        state_repository.save_state(game_snapshot)

    def backup_state_file(self) -> Path | None:
        state_repository = self.state_repository
        return state_repository.backup_state_file()
