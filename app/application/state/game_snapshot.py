from dataclasses import dataclass

from app.application.state.game_record_book import GameRecordBook
from app.model.quiz_catalog import QuizCatalog


@dataclass(frozen=True)
class GameSnapshot:
    quiz_catalog: QuizCatalog
    game_record_book: GameRecordBook
