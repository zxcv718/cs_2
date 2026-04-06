from app.console_interface import ConsoleInterface
from app.model.quiz_catalog import QuizCatalog


class QuizCatalogListingService:
    def __init__(self, console_interface: ConsoleInterface) -> None:
        self.console_interface = console_interface

    def show_quizzes(self, quiz_catalog: QuizCatalog) -> None:
        console_interface = self.console_interface
        console_interface.show_quiz_list(quiz_catalog)
