from app.service.game_runtime_state import GameRuntimeState
from app.service.quiz_catalog_workflow import QuizCatalogWorkflow
from app.service.quiz_play_workflow import QuizPlayWorkflow
from app.ui.console_ui import ConsoleUI


class MenuExecution:
    def __init__(
        self,
        quiz_play_workflow: QuizPlayWorkflow,
        quiz_catalog_workflow: QuizCatalogWorkflow,
    ) -> None:
        self.quiz_play_workflow = quiz_play_workflow
        self.quiz_catalog_workflow = quiz_catalog_workflow

    def play(
        self,
        console_interface: ConsoleUI,
        runtime_state: GameRuntimeState,
    ) -> None:
        quiz_play_workflow = self.quiz_play_workflow
        quiz_play_workflow.play(console_interface, runtime_state)

    def add(self, runtime_state: GameRuntimeState) -> None:
        quiz_catalog_workflow = self.quiz_catalog_workflow
        quiz_catalog_workflow.add(runtime_state)

    def delete(self, runtime_state: GameRuntimeState) -> None:
        quiz_catalog_workflow = self.quiz_catalog_workflow
        quiz_catalog_workflow.delete(runtime_state)

    def show_list(self, runtime_state: GameRuntimeState) -> None:
        quiz_catalog_workflow = self.quiz_catalog_workflow
        quiz_catalog_workflow.show_list(runtime_state)

    def show_best_score(
        self,
        console_interface: ConsoleUI,
        runtime_state: GameRuntimeState,
    ) -> None:
        runtime_state.show_best_score_on(console_interface)

    def persist(self, runtime_state: GameRuntimeState) -> None:
        quiz_catalog_workflow = self.quiz_catalog_workflow
        quiz_catalog_workflow.persist(runtime_state)
