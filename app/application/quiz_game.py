from app.application.quiz_game_runner import QuizGameRunner
from app.application.state.game_runtime_state import GameRuntimeState


class QuizGame:
    def __init__(
        self,
        runtime_state: GameRuntimeState,
        quiz_game_runner: QuizGameRunner,
    ) -> None:
        self.runtime_state = runtime_state
        self.quiz_game_runner = quiz_game_runner

    def initialize_state(self) -> None:
        quiz_game_runner = self.quiz_game_runner
        runtime_state = self.runtime_state
        quiz_game_runner.initialize_state(runtime_state)

    def persist_state(self) -> None:
        quiz_game_runner = self.quiz_game_runner
        runtime_state = self.runtime_state
        quiz_game_runner.persist_state(runtime_state)

    def run(self) -> None:
        quiz_game_runner = self.quiz_game_runner
        runtime_state = self.runtime_state
        quiz_game_runner.run(runtime_state)
