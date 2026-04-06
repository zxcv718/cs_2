from dataclasses import dataclass

from app.application.state.game_record_book import GameRecordBook
from app.model.quiz_catalog import QuizCatalog


@dataclass(frozen=True)
class GameSnapshot:
    _quiz_catalog: QuizCatalog
    _game_record_book: GameRecordBook

    def quiz_catalog(self) -> QuizCatalog:
        return self._quiz_catalog

    def game_record_book(self) -> GameRecordBook:
        return self._game_record_book
