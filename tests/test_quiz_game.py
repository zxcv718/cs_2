import unittest

from quiz import Quiz
from quiz_game import QuizGame


class DummyUI:
    def __init__(self):
        self.messages = []
        self.errors = []

    def show_message(self, message):
        self.messages.append(message)

    def show_error(self, message):
        self.errors.append(message)


class DummyStateManager:
    def __init__(self):
        self.saved = None

    def save_state(self, quizzes, best_score, history=None):
        self.saved = {
            "quizzes": quizzes,
            "best_score": best_score,
            "history": history or [],
        }


class MissingStateManager(DummyStateManager):
    def load_state(self):
        raise FileNotFoundError


class BrokenStateManager(DummyStateManager):
    def load_state(self):
        raise ValueError("broken")


class FailingSaveStateManager(DummyStateManager):
    def save_state(self, quizzes, best_score, history=None):
        raise OSError("save failed")


class QuizGameTestCase(unittest.TestCase):
    def make_game(self, state_manager=None, ui=None):
        return QuizGame(ui or DummyUI(), state_manager or DummyStateManager())

    def test_create_default_quizzes_returns_at_least_five_quizzes(self):
        game = self.make_game()

        quizzes = game.create_default_quizzes()

        self.assertGreaterEqual(len(quizzes), 5)
        self.assertTrue(all(isinstance(q, Quiz) for q in quizzes))

    def test_update_best_score_sets_first_score(self):
        game = self.make_game()
        game.best_score = None

        game.update_best_score(30)

        self.assertEqual(game.best_score, 30)

    def test_update_best_score_replaces_lower_score(self):
        game = self.make_game()
        game.best_score = 20

        game.update_best_score(30)

        self.assertEqual(game.best_score, 30)

    def test_update_best_score_keeps_higher_score(self):
        game = self.make_game()
        game.best_score = 40

        game.update_best_score(30)

        self.assertEqual(game.best_score, 40)

    def test_calculate_score_without_hint(self):
        game = self.make_game()

        score = game.calculate_score(correct_count=4, hint_used_count=0)

        self.assertEqual(score, 40)

    def test_calculate_score_with_hint_penalty(self):
        game = self.make_game()
        game.hint_penalty = 2

        score = game.calculate_score(correct_count=4, hint_used_count=1)

        self.assertEqual(score, 38)

    def test_calculate_score_never_goes_below_zero(self):
        game = self.make_game()
        game.hint_penalty = 20

        score = game.calculate_score(correct_count=1, hint_used_count=1)

        self.assertEqual(score, 0)

    def test_record_history_appends_entry(self):
        game = self.make_game()
        game.history = []

        game.record_history(
            total_questions=5,
            correct_count=4,
            score=38,
            hint_used_count=1,
        )

        self.assertEqual(len(game.history), 1)
        item = game.history[0]
        self.assertEqual(item["total_questions"], 5)
        self.assertEqual(item["correct_count"], 4)
        self.assertEqual(item["score"], 38)
        self.assertEqual(item["hint_used_count"], 1)
        self.assertIn("played_at", item)

    def test_persist_state_delegates_to_state_manager(self):
        game = self.make_game()
        game.quizzes = [Quiz("문제", ["A", "B", "C", "D"], 1)]
        game.best_score = 50
        game.history = []

        game.persist_state()

        self.assertIsNotNone(game.state_manager.saved)
        self.assertEqual(game.state_manager.saved["best_score"], 50)

    def test_persist_state_reports_save_error(self):
        ui = DummyUI()
        game = self.make_game(state_manager=FailingSaveStateManager(), ui=ui)

        game.persist_state()

        self.assertTrue(ui.errors)

    def test_initialize_state_uses_defaults_when_file_missing(self):
        ui = DummyUI()
        game = self.make_game(state_manager=MissingStateManager(), ui=ui)

        game.initialize_state()

        self.assertGreaterEqual(len(game.quizzes), 5)
        self.assertEqual(game.best_score, None)
        self.assertEqual(game.history, [])
        self.assertTrue(ui.messages)

    def test_initialize_state_recovers_on_value_error(self):
        ui = DummyUI()
        game = self.make_game(state_manager=BrokenStateManager(), ui=ui)

        game.initialize_state()

        self.assertGreaterEqual(len(game.quizzes), 5)
        self.assertTrue(ui.errors)


if __name__ == "__main__":
    unittest.main()
