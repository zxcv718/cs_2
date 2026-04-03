from console_ui import ConsoleUI
from constants import STATE_FILE
from quiz_game import QuizGame
from state_manager import StateManager


def main() -> None:
    ui = ConsoleUI()
    state_manager = StateManager(STATE_FILE)
    game = QuizGame(ui, state_manager)
    game.run()


if __name__ == "__main__":
    main()

