import tempfile
import unittest
from pathlib import Path
from typing import Optional, cast
from unittest.mock import patch

import app.config.constants as constants
from app.application.menu_action_dispatcher import MenuActionDispatcher
from app.application.play.best_score_service import BestScore, BestScoreService
from app.application.play.question_count_chooser import QuestionCountChooser
from app.application.play.quiz_history_service import QuizHistoryService
from app.application.play.quiz_partial_result_builder import QuizPartialResultBuilder
from app.application.play.quiz_question_round_service import QuizQuestionRoundService
from app.application.play.quiz_round_coordinator import QuizRoundCoordinator
from app.application.play.quiz_scoring_service import QuizScoringService
from app.application.play.quiz_session_models import AnswerTally, QuizPerformance, QuizSessionInterrupted
from app.application.play.quiz_session_service import QuizSessionService
from app.application.quiz_game import QuizGame
from app.application.quiz_game_execution import QuizGameExecution
from app.application.quiz_game_factory import QuizGameFactory
from app.application.state.default_game_state_factory import DefaultGameStateFactory
from app.application.state.game_bootstrap_service import GameBootstrapService
from app.application.state.game_runtime_state import GameRuntimeState
from app.application.state.game_state_service import GameStateService
from app.console.input import ConsoleInput
from app.console.interface import ConsoleInterface
from app.model.quiz import Quiz
from app.model.quiz_catalog import QuizCatalog, QuizItems
from app.model.quiz_components import (
    AnswerNumber,
    ChoiceDrafts,
    HintText,
    QuestionText,
    QuizDraft,
    QuizDraftPrompt,
    QuizDraftSolution,
)
from app.model.quiz_factory import QuizFactory
from app.model.quiz_selection import QuizSelection, QuizSelectionItems
from app.repository.quiz_payload_mapper import QuizPayloadMapper
from app.repository.state_payload_mapper import StatePayloadMapper
from app.repository.state_repository import StateRepository
from app.service.quiz_metrics import (
    CorrectAnswerCount,
    DeleteMenuAvailability,
    DisplayIndex,
    HintUsageCount,
    MenuChoice,
    QuestionCount,
    ScoreValue,
)


def create_quiz(
    question: str,
    choices: list[str],
    answer: int,
    hint: str | None = None,
) -> Quiz:
    quiz_draft = QuizDraft(
        prompt=QuizDraftPrompt(
            QuestionText.from_raw(question),
            ChoiceDrafts.from_iterable(choices),
        ),
        solution=QuizDraftSolution(
            AnswerNumber.from_raw(answer),
            HintText.from_raw(hint),
        ),
    )
    return QuizFactory().create(quiz_draft)


def payload_dictionary(snapshot) -> dict:
    state_mapper = StatePayloadMapper()
    state_payload = state_mapper.to_state_payload(snapshot)
    return cast(dict, state_mapper._payload_dictionary(state_payload))


def snapshot_from_dictionary(payload: dict):
    state_mapper = StatePayloadMapper()
    state_payload = state_mapper._state_payload(payload)
    return state_mapper.from_state_payload(state_payload)


def optional_score(best_score: BestScore) -> int | None:
    score_value = best_score.score_value
    if score_value is None:
        return None
    return int(score_value)


class DummyConsoleInterface(ConsoleInterface):
    def __init__(self):
        self.messages = []
        self.errors = []

    def show_menu(self, delete_menu_availability: DeleteMenuAvailability):
        return None

    def show_message(self, message):
        self.messages.append(message)

    def show_error(self, message):
        self.errors.append(message)


class PlayMenuOnceConsoleInterface(DummyConsoleInterface):
    def request_menu_choice(self, min_value, max_value):
        return MenuChoice(constants.MENU_PLAY)

    def show_result(self, correct_count, score, total_questions, hint_used_count=0):
        return None


class InterruptingSessionConsoleInterface(DummyConsoleInterface):
    def __init__(self):
        super().__init__()
        self.answer_call_count = 0

    def request_valid_number(self, prompt, min_value, max_value):
        return 2

    def show_question(self, quiz, index, total):
        return None

    def request_answer_or_hint(self, prompt, min_value=1, max_value=4):
        self.answer_call_count += 1
        if self.answer_call_count == 1:
            return 1
        raise KeyboardInterrupt


class HintThenCorrectConsoleInterface(DummyConsoleInterface):
    def __init__(self):
        super().__init__()
        self.answer_call_count = 0

    def show_question(self, quiz, index, total):
        return None

    def request_answer_or_hint(self, prompt, min_value=1, max_value=4):
        self.answer_call_count += 1
        if self.answer_call_count == 1:
            return constants.HINT_COMMAND_VALUE
        return 2


class AnswerThenHintThenInterruptConsoleInterface(DummyConsoleInterface):
    def __init__(self):
        super().__init__()
        self.answer_call_count = 0

    def request_valid_number(self, prompt, min_value, max_value):
        return 2

    def show_question(self, quiz, index, total):
        return None

    def request_answer_or_hint(self, prompt, min_value=1, max_value=4):
        self.answer_call_count += 1
        if self.answer_call_count == 1:
            return 1
        if self.answer_call_count == 2:
            return constants.HINT_COMMAND_VALUE
        raise KeyboardInterrupt


class ManyHintsThenCorrectConsoleInterface(DummyConsoleInterface):
    def __init__(self, hint_attempt_count: int, final_answer: int):
        super().__init__()
        self.hint_attempt_count = hint_attempt_count
        self.final_answer = final_answer

    def show_question(self, quiz, index, total):
        return None

    def request_answer_or_hint(self, prompt, min_value=1, max_value=4):
        if self.hint_attempt_count > 0:
            self.hint_attempt_count -= 1
            return constants.HINT_COMMAND_VALUE
        return self.final_answer


class RepeatingMenuConsoleInterface(DummyConsoleInterface):
    def request_menu_choice(self, min_value, max_value):
        return MenuChoice(constants.MENU_PLAY)


class NoOpBootstrapService:
    def initialize(self, runtime_state, console_interface):
        return None


class CountingMenuDispatcher:
    def __init__(self, continue_count: int):
        self.continue_count = continue_count

    def dispatch(self, menu_choice, runtime_state, delete_menu_availability, console_interface):
        if self.continue_count == 0:
            return False
        self.continue_count -= 1
        return True

    def persist(self, runtime_state):
        return None

    def handle_interrupted_session(self, runtime_state, result):
        return None

    def handle_interrupted_program(self, runtime_state):
        return None


class AlwaysIncorrectRoundService:
    def play_round(self, quiz, index, total_questions):
        return AnswerTally(
            CorrectAnswerCount(0),
            HintUsageCount(0),
        )


class DummyStateRepository(StateRepository):
    def __init__(self):
        quiz_mapper = QuizPayloadMapper()
        self.saved = None
        payload_item = quiz_mapper.to_payload_item(
            create_quiz("기본 문제", ["A", "B", "C", "D"], 1)
        )
        self.loaded_state = snapshot_from_dictionary(
            {
                "quizzes": [quiz_mapper._payload_dictionary(payload_item)],
                "best_score": 10,
                "history": [],
            }
        )

    def load_state(self):
        return self.loaded_state

    def save_state(self, game_snapshot):
        self.saved = payload_dictionary(game_snapshot)

    def backup_state_file(self):
        return None


class MissingStateRepository(DummyStateRepository):
    def load_state(self):
        raise FileNotFoundError


class BrokenStateRepository(DummyStateRepository):
    def load_state(self):
        raise ValueError("broken")


class FailingSaveStateRepository(DummyStateRepository):
    def save_state(self, game_snapshot):
        raise OSError("save failed")


class DeterministicQuizSessionService(QuizSessionService):
    def _select_quizzes(self, quiz_catalog, question_count):
        selection_items = QuizSelectionItems.from_iterable(
            list(quiz_catalog)[: int(question_count)]
        )
        return QuizSelection(selection_items)


class DefaultGameStateFactoryTestCase(unittest.TestCase):
    def test_create_state_returns_at_least_five_quizzes(self):
        factory = DefaultGameStateFactory()

        state = factory.create_state()
        quiz_catalog = state.quiz_catalog
        record_book = state.game_record_book

        self.assertGreaterEqual(len(quiz_catalog), 5)
        self.assertIsNone(optional_score(record_book.best_score))
        self.assertEqual(len(record_book.play_history), 0)
        self.assertTrue(all(isinstance(q, Quiz) for q in quiz_catalog))


class GameStateServiceTestCase(unittest.TestCase):
    def test_load_and_save_delegate_to_repository(self):
        repository = DummyStateRepository()
        service = GameStateService(repository)

        loaded_state = service.load_state()
        service.save_state(loaded_state)

        self.assertIsNotNone(repository.saved)


class BestScoreServiceTestCase(unittest.TestCase):
    def test_update_best_score_sets_first_score(self):
        service = BestScoreService()

        best_score_update = service.update_best_score(BestScore.empty(), ScoreValue(30))
        best_score = best_score_update.best_score

        self.assertEqual(optional_score(best_score), 30)
        self.assertTrue(best_score_update.record_update_status.updated)

    def test_update_best_score_replaces_lower_score(self):
        service = BestScoreService()

        best_score_update = service.update_best_score(
            BestScore.from_optional_int(20),
            ScoreValue(30),
        )
        best_score = best_score_update.best_score

        self.assertEqual(optional_score(best_score), 30)
        self.assertTrue(best_score_update.record_update_status.updated)

    def test_update_best_score_keeps_higher_score(self):
        service = BestScoreService()

        best_score_update = service.update_best_score(
            BestScore.from_optional_int(40),
            ScoreValue(30),
        )
        best_score = best_score_update.best_score

        self.assertEqual(optional_score(best_score), 40)
        self.assertFalse(best_score_update.record_update_status.updated)


class QuizScoringServiceTestCase(unittest.TestCase):
    def test_calculate_score_without_hint(self):
        service = QuizScoringService()

        score = service.calculate_score(
            correct_count=CorrectAnswerCount(4),
            hint_used_count=HintUsageCount(0),
        )

        self.assertEqual(int(score), 40)

    def test_calculate_score_with_hint_penalty(self):
        service = QuizScoringService(hint_penalty=2)

        score = service.calculate_score(
            correct_count=CorrectAnswerCount(4),
            hint_used_count=HintUsageCount(1),
        )

        self.assertEqual(int(score), 38)

    def test_calculate_score_never_goes_below_zero(self):
        service = QuizScoringService(hint_penalty=20)

        score = service.calculate_score(
            correct_count=CorrectAnswerCount(1),
            hint_used_count=HintUsageCount(1),
        )

        self.assertEqual(int(score), 0)


class QuizHistoryServiceTestCase(unittest.TestCase):
    def test_create_entry_returns_expected_fields(self):
        service = QuizHistoryService()
        result = QuizPerformance(
            QuestionCount(5),
            AnswerTally(
                CorrectAnswerCount(4),
                HintUsageCount(1),
            ),
        )

        entry = service.create_entry(result, score_value=ScoreValue(38))

        scored_performance = entry.scored_performance
        quiz_performance = scored_performance.quiz_performance
        answer_tally = quiz_performance.answer_tally
        self.assertEqual(int(quiz_performance.total_questions), 5)
        self.assertEqual(int(answer_tally.correct_answers), 4)
        self.assertEqual(int(scored_performance.score_value), 38)
        self.assertEqual(int(answer_tally.hint_usages), 1)
        self.assertTrue(str(entry.played_at))


class QuestionCountChooserTestCase(unittest.TestCase):
    def test_choose_question_count_delegates_to_ui(self):
        console_interface = InterruptingSessionConsoleInterface()
        service = QuestionCountChooser(console_interface)

        question_count = service.choose_question_count(QuestionCount(5))

        self.assertEqual(int(question_count), 2)


class QuizQuestionRoundServiceTestCase(unittest.TestCase):
    def test_play_round_counts_hint_and_correct_answer(self):
        console_interface = HintThenCorrectConsoleInterface()
        service = QuizQuestionRoundService(console_interface)
        quiz = create_quiz("문제", ["A", "B", "C", "D"], 2, hint="힌트")

        result = service.play_round(
            quiz,
            index=DisplayIndex(1),
            total_questions=QuestionCount(3),
        )

        self.assertEqual(int(result.correct_answers), 1)
        self.assertEqual(int(result.hint_usages), 1)
        self.assertTrue(console_interface.messages)

    def test_play_round_handles_many_retry_inputs_without_recursion_error(self):
        console_interface = ManyHintsThenCorrectConsoleInterface(
            hint_attempt_count=1200,
            final_answer=1,
        )
        service = QuizQuestionRoundService(console_interface)
        quiz = create_quiz("문제", ["A", "B", "C", "D"], 1)

        result = service.play_round(
            quiz,
            index=DisplayIndex(1),
            total_questions=QuestionCount(1),
        )

        self.assertEqual(int(result.correct_answers), 1)
        self.assertEqual(len(console_interface.errors), 1200)


class QuizPartialResultBuilderTestCase(unittest.TestCase):
    def test_build_interrupted_result_returns_none_before_any_answer(self):
        builder = QuizPartialResultBuilder()
        answer_tally = AnswerTally(
            CorrectAnswerCount(0),
            HintUsageCount(0),
        )

        result = builder.build_interrupted_result(
            total_questions=QuestionCount(3),
            answer_tally=answer_tally,
            answered_question_count=QuestionCount(0),
        )

        self.assertIsNone(result)


class QuizSessionServiceTestCase(unittest.TestCase):
    def test_play_raises_interrupted_with_partial_result_after_answer(self):
        console_interface = InterruptingSessionConsoleInterface()
        service = DeterministicQuizSessionService(console_interface)
        quizzes = [
            create_quiz("문제1", ["A", "B", "C", "D"], 1),
            create_quiz("문제2", ["A", "B", "C", "D"], 2),
        ]
        quiz_catalog = QuizCatalog(QuizItems.from_iterable(quizzes))

        with self.assertRaises(QuizSessionInterrupted) as context:
            service.play(quiz_catalog)

        partial_performance = context.exception.partial_performance

        self.assertIsNotNone(partial_performance)
        assert partial_performance is not None
        answer_tally = partial_performance.answer_tally
        self.assertEqual(int(partial_performance.total_questions), 2)
        self.assertEqual(int(answer_tally.correct_answers), 1)
        self.assertEqual(int(answer_tally.hint_usages), 0)

    def test_play_keeps_hint_count_when_interrupted_after_showing_hint(self):
        console_interface = AnswerThenHintThenInterruptConsoleInterface()
        service = DeterministicQuizSessionService(console_interface)
        quizzes = [
            create_quiz("문제1", ["A", "B", "C", "D"], 1, hint="힌트1"),
            create_quiz("문제2", ["A", "B", "C", "D"], 2, hint="힌트2"),
        ]
        quiz_catalog = QuizCatalog(QuizItems.from_iterable(quizzes))

        with self.assertRaises(QuizSessionInterrupted) as context:
            service.play(quiz_catalog)

        partial_performance = context.exception.partial_performance

        self.assertIsNotNone(partial_performance)
        assert partial_performance is not None
        answer_tally = partial_performance.answer_tally
        self.assertEqual(int(answer_tally.correct_answers), 1)
        self.assertEqual(int(answer_tally.hint_usages), 1)


class ConsoleInputTestCase(unittest.TestCase):
    def test_request_non_empty_text_handles_many_invalid_attempts_without_recursion_error(self):
        errors = []
        console_input = ConsoleInput(errors.append)
        responses = [""] * 1200 + ["정상 입력"]

        with patch("builtins.input", side_effect=responses):
            result = console_input.request_non_empty_text("입력: ")

        self.assertEqual(result, "정상 입력")
        self.assertEqual(len(errors), 1200)


class QuizRoundCoordinatorTestCase(unittest.TestCase):
    def test_play_selected_quizzes_handles_large_quiz_count_without_recursion_error(self):
        coordinator = QuizRoundCoordinator(
            cast(QuizQuestionRoundService, AlwaysIncorrectRoundService()),
            QuizPartialResultBuilder(),
        )
        quizzes = [
            create_quiz(f"문제{i}", ["A", "B", "C", "D"], 1)
            for i in range(1200)
        ]

        selection_items = QuizSelectionItems.from_iterable(quizzes)
        result = coordinator.play_selected_quizzes(QuizSelection(selection_items))

        answer_tally = result.answer_tally
        self.assertEqual(int(result.total_questions), 1200)
        self.assertEqual(int(answer_tally.correct_answers), 0)
        self.assertEqual(int(answer_tally.hint_usages), 0)


class QuizGameExecutionTestCase(unittest.TestCase):
    def test_run_handles_many_menu_cycles_without_recursion_error(self):
        dispatcher = CountingMenuDispatcher(continue_count=1200)
        execution = QuizGameExecution(
            cast(GameBootstrapService, NoOpBootstrapService()),
            cast(MenuActionDispatcher, dispatcher),
        )

        execution.run(
            GameRuntimeState(),
            RepeatingMenuConsoleInterface(),
        )

        self.assertEqual(dispatcher.continue_count, 0)


class QuizGameTestCase(unittest.TestCase):
    def make_game(
        self,
        state_repository: Optional[DummyStateRepository] = None,
        console_interface_override: Optional[DummyConsoleInterface] = None,
    ) -> QuizGame:
        console_interface = DummyConsoleInterface()
        if console_interface_override is not None:
            console_interface = console_interface_override

        repository = DummyStateRepository()
        if state_repository is not None:
            repository = state_repository

        return QuizGameFactory().create(console_interface, repository)

    def test_persist_state_delegates_to_state_repository(self):
        repository = DummyStateRepository()
        game = self.make_game(state_repository=repository)
        quiz_mapper = QuizPayloadMapper()
        quiz = create_quiz("문제", ["A", "B", "C", "D"], 1)
        payload_item = quiz_mapper.to_payload_item(quiz)
        game.runtime_state.restore(
            snapshot_from_dictionary(
                {
                    "quizzes": [quiz_mapper._payload_dictionary(payload_item)],
                    "best_score": 50,
                    "history": [],
                }
            )
        )

        game.persist_state()

        self.assertIsNotNone(repository.saved)
        assert repository.saved is not None
        self.assertEqual(repository.saved["best_score"], 50)

    def test_persist_state_reports_save_error(self):
        console_interface = DummyConsoleInterface()
        game = self.make_game(
            state_repository=FailingSaveStateRepository(),
            console_interface_override=console_interface,
        )

        game.persist_state()

        self.assertTrue(console_interface.errors)

    def test_initialize_state_uses_defaults_when_file_missing(self):
        console_interface = DummyConsoleInterface()
        game = self.make_game(
            state_repository=MissingStateRepository(),
            console_interface_override=console_interface,
        )

        game.initialize_state()

        self.assertGreaterEqual(len(game.runtime_state.quiz_catalog), 5)
        self.assertIsNone(optional_score(game.runtime_state.record_book.best_score))
        self.assertTrue(console_interface.messages)

    def test_initialize_state_recovers_on_value_error(self):
        console_interface = DummyConsoleInterface()
        game = self.make_game(
            state_repository=BrokenStateRepository(),
            console_interface_override=console_interface,
        )

        game.initialize_state()

        self.assertGreaterEqual(len(game.runtime_state.quiz_catalog), 5)
        self.assertTrue(console_interface.errors)

    def test_initialize_state_preserves_invalid_file_before_restoring_defaults(self):
        broken_text = "{broken json"
        with tempfile.TemporaryDirectory() as temp_dir:
            state_file = Path(temp_dir) / "state.json"
            state_file.write_text(broken_text, encoding="utf-8")
            console_interface = DummyConsoleInterface()
            game = QuizGameFactory().create(console_interface, StateRepository(state_file))

            game.initialize_state()

            backup_file = Path(temp_dir) / "state.json.bak"
            self.assertTrue(backup_file.exists())
            self.assertEqual(
                backup_file.read_text(encoding="utf-8"),
                broken_text,
            )
            restored_state = StateRepository(state_file).load_state()
            self.assertGreaterEqual(len(restored_state.quiz_catalog), 5)
            self.assertTrue(console_interface.errors)

    def test_run_persists_partial_result_when_session_is_interrupted(self):
        console_interface = PlayMenuOnceConsoleInterface()
        repository = DummyStateRepository()
        quiz_mapper = QuizPayloadMapper()
        repository.loaded_state = snapshot_from_dictionary(
            {
                "quizzes": [
                    quiz_mapper._payload_dictionary(
                        quiz_mapper.to_payload_item(
                            create_quiz("문제1", ["A", "B", "C", "D"], 1)
                        )
                    ),
                    quiz_mapper._payload_dictionary(
                        quiz_mapper.to_payload_item(
                            create_quiz("문제2", ["A", "B", "C", "D"], 2)
                        )
                    ),
                ],
                "best_score": None,
                "history": [],
            }
        )
        game = self.make_game(
            state_repository=repository,
            console_interface_override=console_interface,
        )

        partial_performance = QuizPerformance(
            QuestionCount(2),
            AnswerTally(
                CorrectAnswerCount(1),
                HintUsageCount(0),
            ),
        )

        with patch.object(
            QuizSessionService,
            "play",
            side_effect=QuizSessionInterrupted(partial_performance),
        ):
            game.run()

        self.assertIsNotNone(repository.saved)
        assert repository.saved is not None
        self.assertEqual(repository.saved["best_score"], 10)
        self.assertEqual(len(repository.saved["history"]), 1)
        self.assertEqual(repository.saved["history"][0]["correct_count"], 1)
        self.assertIn(constants.MESSAGE_INTERRUPTED_EXIT, console_interface.messages)


if __name__ == "__main__":
    unittest.main()
