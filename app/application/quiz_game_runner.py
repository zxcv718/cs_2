from app.application.quiz_game_execution import QuizGameExecution
from app.application.state.game_runtime_state import GameRuntimeState
from app.console.interface import ConsoleInterface


class QuizGameRunner:
    def __init__(
        self,
        console_interface: ConsoleInterface,
        quiz_game_execution: QuizGameExecution,
    ) -> None:
        self.console_interface = console_interface
        self.quiz_game_execution = quiz_game_execution

    def initialize_state(self, runtime_state: GameRuntimeState) -> None:
        quiz_game_execution = self.quiz_game_execution
        console_interface = self.console_interface
        quiz_game_execution.initialize_state(
            runtime_state,
            console_interface,
        )

    def persist_state(self, runtime_state: GameRuntimeState) -> None:
        quiz_game_execution = self.quiz_game_execution
        quiz_game_execution.persist_state(runtime_state)

    def run(self, runtime_state: GameRuntimeState) -> None:
        quiz_game_execution = self.quiz_game_execution
        console_interface = self.console_interface
        quiz_game_execution.run(
            runtime_state,
            console_interface,
        )
