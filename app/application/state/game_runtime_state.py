from dataclasses import dataclass, field

from app.application.play.best_score_service import BestScore, BestScoreUpdate
from app.application.state.game_record_book import GameRecordBook
from app.application.state.game_snapshot import GameSnapshot
from app.application.state.quiz_history_entry import QuizHistoryEntry
from app.model.quiz_catalog import QuizCatalog


@dataclass
class GameRuntimeState:
    quiz_catalog: QuizCatalog = field(default_factory=QuizCatalog)
    record_book: GameRecordBook = field(default_factory=GameRecordBook.create_empty)

    def restore(self, game_snapshot: GameSnapshot) -> None:
        self.quiz_catalog = game_snapshot.quiz_catalog
        self.record_book = game_snapshot.game_record_book

    def saveable_snapshot(self) -> GameSnapshot:
        return GameSnapshot(self.quiz_catalog, self.record_book)

    def record_play_result(
        self,
        best_score_update: BestScoreUpdate,
        history_entry: QuizHistoryEntry,
    ) -> None:
        record_book = self.record_book
        record_book.record(best_score_update, history_entry)
