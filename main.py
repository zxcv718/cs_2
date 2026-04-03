from app.config.constants import STATE_FILE
from app.service.quiz_game import QuizGame
from app.repository.state_repository import StateRepository
from app.ui.console_ui import ConsoleUI


def main() -> None:
    ui = ConsoleUI()
    state_repository = StateRepository(STATE_FILE)
    game = QuizGame(ui, state_repository)
    game.run()


if __name__ == "__main__":
    main()
