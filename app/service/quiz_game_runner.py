from app.service.game_runtime_state import GameRuntimeState
from app.service.quiz_game_execution import QuizGameExecution
from app.ui.console_ui import ConsoleUI


class QuizGameRunner:
    def __init__(
        self,
        console_interface: ConsoleUI,
        quiz_game_execution: QuizGameExecution,
    ) -> None:
        self.console_interface = console_interface
        self.quiz_game_execution = quiz_game_execution

    def initialize_state(self, runtime_state: GameRuntimeState) -> None:
        self.quiz_game_execution.initialize_state(
            runtime_state,
            self.console_interface,
        )

    def persist_state(self, runtime_state: GameRuntimeState) -> None:
        self.quiz_game_execution.persist_state(runtime_state)

    def run(self, runtime_state: GameRuntimeState) -> None:
        self.quiz_game_execution.run(
            runtime_state,
            self.console_interface,
        )
