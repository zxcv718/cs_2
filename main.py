from app.application.quiz_game import QuizGame
from app.infrastructure.constants import STATE_FILE
from app.infrastructure.state_manager import StateManager
from app.ui.console_ui import ConsoleUI


def main() -> None:
    ui = ConsoleUI()
    state_manager = StateManager(STATE_FILE)
    game = QuizGame(ui, state_manager)
    game.run()


if __name__ == "__main__":
    main()
