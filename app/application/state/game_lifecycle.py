from dataclasses import dataclass

from app.application.state.game_record_book import GameRecordBook


@dataclass
class GameLifecycle:
    record_book: GameRecordBook
    initialized: bool

    @classmethod
    def create_uninitialized(cls) -> "GameLifecycle":
        return cls(GameRecordBook.create_empty(), False)

    def mark_initialized(self) -> None:
        self.initialized = True
