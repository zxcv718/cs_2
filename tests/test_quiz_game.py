import tempfile
import unittest
from pathlib import Path
from typing import Optional, cast
from unittest.mock import patch

import app.config.constants as constants
from app.application.menu_action_dispatcher import MenuActionDispatcher
from app.application.play.best_score_service import BestScoreService
from app.application.play.question_count_chooser import QuestionCountChooser
from app.application.play.quiz_history_service import QuizHistoryService
from app.application.play.quiz_partial_result_builder import QuizPartialResultBuilder
from app.application.play.quiz_question_round_service import (
    QuizQuestionRoundResult,
    QuizQuestionRoundService,
)
from app.application.play.quiz_round_coordinator import QuizRoundCoordinator
from app.application.play.quiz_scoring_service import QuizScoringService
from app.application.play.quiz_session_models import QuizSessionInterrupted, QuizSessionResult
from app.application.play.quiz_session_service import QuizSessionService
from app.application.quiz_game import QuizGame
from app.application.quiz_game_execution import QuizGameExecution
from app.application.state.default_game_state_factory import DefaultGameStateFactory
from app.application.state.game_bootstrap_service import GameBootstrapService
from app.application.state.game_runtime_state import GameRuntimeState
from app.application.state.game_state_service import GameStateService
from app.console.input import ConsoleInput
from app.console.interface import ConsoleInterface
from app.model.quiz import Quiz
from app.model.quiz_catalog import QuizCatalog
from app.model.quiz_factory import QuizFactory
from app.repository.state_repository import StateRepository
from app.service.quiz_metrics import (
    CorrectAnswerCount,
    DisplayIndex,
    HintUsageCount,
    MenuChoice,
    QuestionCount,
    ScoreValue,
)


# 실제 입력 대신 테스트에서 사용할 가짜 UI입니다.
class DummyConsoleInterface(ConsoleInterface):
    def __init__(self):
        self.messages = []
        self.errors = []

    # 출력된 일반 메시지를 리스트에 모읍니다.
    def show_message(self, message):
        self.messages.append(message)

    # 출력된 오류 메시지를 리스트에 모읍니다.
    def show_error(self, message):
        self.errors.append(message)


class PlayMenuOnceConsoleInterface(DummyConsoleInterface):
    def show_menu(self, has_delete=False):
        return None

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
    def show_menu(self, has_delete=False):
        return None

    def request_menu_choice(self, min_value, max_value):
        return MenuChoice(constants.MENU_PLAY)


class NoOpBootstrapService:
    def initialize(self, runtime_state, console_interface):
        return None


class CountingMenuDispatcher:
    def __init__(self, continue_count: int):
        self.continue_count = continue_count

    def dispatch(self, menu_choice, runtime_state, has_delete, console_interface):
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
        return QuizQuestionRoundResult(
            CorrectAnswerCount(0),
            HintUsageCount(0),
        )


# 실제 파일 대신 메모리에 저장 결과를 남기는 가짜 저장소입니다.
class DummyStateRepository(StateRepository):
    def __init__(self):
        factory = QuizFactory()
        self.saved = None
        self.loaded_state = {
            "quizzes": [factory.create("기본 문제", ["A", "B", "C", "D"], 1)],
            "best_score": 10,
            "history": [],
        }

    # 읽기 요청이 오면 미리 준비한 상태를 반환합니다.
    def load_state(self):
        return self.loaded_state

    # 저장 요청이 오면 마지막 저장 내용을 기록합니다.
    def save_state(self, quizzes, best_score, history=None):
        self.saved = {
            "quizzes": quizzes,
            "best_score": best_score,
            "history": history or [],
        }

    def backup_state_file(self):
        return None


# 파일이 없을 때의 상황을 흉내 냅니다.
class MissingStateRepository(DummyStateRepository):
    def load_state(self):
        raise FileNotFoundError


# 파일 내용이 잘못된 상황을 흉내 냅니다.
class BrokenStateRepository(DummyStateRepository):
    def load_state(self):
        raise ValueError("broken")


# 저장 실패 상황을 흉내 냅니다.
class FailingSaveStateRepository(DummyStateRepository):
    def save_state(self, quizzes, best_score, history=None):
        raise OSError("save failed")


class DeterministicQuizSessionService(QuizSessionService):
    def _select_quizzes(self, quiz_catalog, question_count):
        return list(quiz_catalog)[: int(question_count)]


class InterruptedSessionService(QuizSessionService):
    def __init__(self, partial_result):
        self.partial_result = partial_result

    def play(self, quiz_catalog):
        raise QuizSessionInterrupted(self.partial_result)


# 기본 상태 생성 책임을 테스트합니다.
class DefaultGameStateFactoryTestCase(unittest.TestCase):
    # 기본 상태가 최소 5개의 퀴즈와 함께 만들어지는지 확인합니다.
    def test_create_state_returns_at_least_five_quizzes(self):
        factory = DefaultGameStateFactory()

        state = factory.create_state()

        self.assertGreaterEqual(len(state["quizzes"]), 5)
        self.assertIsNone(state["best_score"])
        self.assertEqual(state["history"], [])
        self.assertTrue(all(isinstance(q, Quiz) for q in state["quizzes"]))


# GameStateService가 저장소 위임만 담당하는지 테스트합니다.
class GameStateServiceTestCase(unittest.TestCase):
    # 상태 읽기와 저장이 저장소에 위임되는지 확인합니다.
    def test_load_and_save_delegate_to_repository(self):
        repository = DummyStateRepository()
        service = GameStateService(repository)

        loaded_state = service.load_state()
        service.save_state(
            loaded_state["quizzes"],
            loaded_state["best_score"],
            loaded_state["history"],
        )

        self.assertEqual(loaded_state, repository.loaded_state)
        self.assertIsNotNone(repository.saved)


# 최고 점수 갱신 규칙만 담당하는 서비스를 테스트합니다.
class BestScoreServiceTestCase(unittest.TestCase):
    # 첫 플레이 점수는 바로 최고 점수가 되어야 합니다.
    def test_update_best_score_sets_first_score(self):
        service = BestScoreService()

        best_score, is_new_record = service.update_best_score(None, ScoreValue(30))

        self.assertEqual(int(best_score), 30)
        self.assertTrue(is_new_record)

    # 더 높은 점수가 나오면 최고 점수가 바뀌어야 합니다.
    def test_update_best_score_replaces_lower_score(self):
        service = BestScoreService()

        best_score, is_new_record = service.update_best_score(
            ScoreValue(20),
            ScoreValue(30),
        )

        self.assertEqual(int(best_score), 30)
        self.assertTrue(is_new_record)

    # 더 낮은 점수는 최고 점수를 바꾸면 안 됩니다.
    def test_update_best_score_keeps_higher_score(self):
        service = BestScoreService()

        best_score, is_new_record = service.update_best_score(
            ScoreValue(40),
            ScoreValue(30),
        )

        self.assertEqual(int(best_score), 40)
        self.assertFalse(is_new_record)


# 점수 계산 규칙만 담당하는 서비스를 테스트합니다.
class QuizScoringServiceTestCase(unittest.TestCase):
    # 힌트를 쓰지 않으면 정답 수만큼 점수가 올라야 합니다.
    def test_calculate_score_without_hint(self):
        service = QuizScoringService()

        score = service.calculate_score(
            correct_count=CorrectAnswerCount(4),
            hint_used_count=HintUsageCount(0),
        )

        self.assertEqual(int(score), 40)

    # 힌트를 쓰면 감점이 반영되어야 합니다.
    def test_calculate_score_with_hint_penalty(self):
        service = QuizScoringService(hint_penalty=2)

        score = service.calculate_score(
            correct_count=CorrectAnswerCount(4),
            hint_used_count=HintUsageCount(1),
        )

        self.assertEqual(int(score), 38)

    # 감점이 커도 최종 점수는 0점 아래로 내려가면 안 됩니다.
    def test_calculate_score_never_goes_below_zero(self):
        service = QuizScoringService(hint_penalty=20)

        score = service.calculate_score(
            correct_count=CorrectAnswerCount(1),
            hint_used_count=HintUsageCount(1),
        )

        self.assertEqual(int(score), 0)


# 플레이 결과를 history 형식으로 바꾸는 서비스를 테스트합니다.
class QuizHistoryServiceTestCase(unittest.TestCase):
    # 플레이 결과가 history용 딕셔너리로 잘 바뀌는지 확인합니다.
    def test_create_entry_returns_expected_fields(self):
        service = QuizHistoryService()
        result = QuizSessionResult(
            total_questions=QuestionCount(5),
            correct_count=CorrectAnswerCount(4),
            hint_used_count=HintUsageCount(1),
        )

        item = service.create_entry(result, score=ScoreValue(38))

        self.assertEqual(item["total_questions"], 5)
        self.assertEqual(item["correct_count"], 4)
        self.assertEqual(item["score"], 38)
        self.assertEqual(item["hint_used_count"], 1)
        self.assertIn("played_at", item)


class QuestionCountChooserTestCase(unittest.TestCase):
    def test_choose_question_count_delegates_to_ui(self):
        console_interface = InterruptingSessionConsoleInterface()
        service = QuestionCountChooser(console_interface)

        question_count = service.choose_question_count(5)

        self.assertEqual(int(question_count), 2)


class QuizQuestionRoundServiceTestCase(unittest.TestCase):
    def test_play_round_counts_hint_and_correct_answer(self):
        console_interface = HintThenCorrectConsoleInterface()
        service = QuizQuestionRoundService(console_interface)
        quiz = QuizFactory().create("문제", ["A", "B", "C", "D"], 2, hint="힌트")

        result = service.play_round(
            quiz,
            index=DisplayIndex(1),
            total_questions=QuestionCount(3),
        )

        self.assertEqual(int(result.correct_count), 1)
        self.assertEqual(int(result.hint_used_count), 1)
        self.assertTrue(console_interface.messages)

    def test_play_round_handles_many_retry_inputs_without_recursion_error(self):
        console_interface = ManyHintsThenCorrectConsoleInterface(
            hint_attempt_count=1200,
            final_answer=1,
        )
        service = QuizQuestionRoundService(console_interface)
        quiz = QuizFactory().create("문제", ["A", "B", "C", "D"], 1)

        result = service.play_round(
            quiz,
            index=DisplayIndex(1),
            total_questions=QuestionCount(1),
        )

        self.assertEqual(int(result.correct_count), 1)
        self.assertEqual(len(console_interface.errors), 1200)


class QuizPartialResultBuilderTestCase(unittest.TestCase):
    def test_build_interrupted_result_returns_none_before_any_answer(self):
        builder = QuizPartialResultBuilder()

        result = builder.build_interrupted_result(
            total_questions=QuestionCount(3),
            correct_count=CorrectAnswerCount(0),
            hint_used_count=HintUsageCount(0),
            answered_question_count=QuestionCount(0),
        )

        self.assertIsNone(result)


class QuizSessionServiceTestCase(unittest.TestCase):
    def test_play_raises_interrupted_with_partial_result_after_answer(self):
        console_interface = InterruptingSessionConsoleInterface()
        service = DeterministicQuizSessionService(console_interface)
        factory = QuizFactory()
        quizzes = [
            factory.create("문제1", ["A", "B", "C", "D"], 1),
            factory.create("문제2", ["A", "B", "C", "D"], 2),
        ]
        quiz_catalog = QuizCatalog.from_items(quizzes)

        with self.assertRaises(QuizSessionInterrupted) as context:
            service.play(quiz_catalog)

        partial_result = context.exception.partial_result

        self.assertIsNotNone(partial_result)
        assert partial_result is not None
        self.assertEqual(int(partial_result.total_questions), 2)
        self.assertEqual(int(partial_result.correct_count), 1)
        self.assertEqual(int(partial_result.hint_used_count), 0)

    def test_play_keeps_hint_count_when_interrupted_after_showing_hint(self):
        console_interface = AnswerThenHintThenInterruptConsoleInterface()
        service = DeterministicQuizSessionService(console_interface)
        factory = QuizFactory()
        quizzes = [
            factory.create("문제1", ["A", "B", "C", "D"], 1, hint="힌트1"),
            factory.create("문제2", ["A", "B", "C", "D"], 2, hint="힌트2"),
        ]
        quiz_catalog = QuizCatalog.from_items(quizzes)

        with self.assertRaises(QuizSessionInterrupted) as context:
            service.play(quiz_catalog)

        partial_result = context.exception.partial_result

        self.assertIsNotNone(partial_result)
        assert partial_result is not None
        self.assertEqual(int(partial_result.correct_count), 1)
        self.assertEqual(int(partial_result.hint_used_count), 1)


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
        factory = QuizFactory()
        quizzes = [
            factory.create(f"문제{i}", ["A", "B", "C", "D"], 1)
            for i in range(1200)
        ]

        result = coordinator.play_selected_quizzes(quizzes)

        self.assertEqual(int(result.total_questions), 1200)
        self.assertEqual(int(result.correct_count), 0)
        self.assertEqual(int(result.hint_used_count), 0)


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


# QuizGame이 하위 서비스를 제대로 호출하는지 테스트합니다.
class QuizGameTestCase(unittest.TestCase):
    # 기본 가짜 객체를 붙여 게임 객체를 쉽게 만듭니다.
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

        return QuizGame(console_interface, repository)

    # persist_state가 저장소에 저장을 위임하는지 확인합니다.
    def test_persist_state_delegates_to_state_repository(self):
        repository = DummyStateRepository()
        game = self.make_game(state_repository=repository)
        game.runtime_state.restore(
            [QuizFactory().create("문제", ["A", "B", "C", "D"], 1)],
            50,
            [],
        )

        game.persist_state()

        self.assertIsNotNone(repository.saved)
        assert repository.saved is not None
        self.assertEqual(repository.saved["best_score"], 50)

    # 저장 실패 시 UI에 오류를 보여줘야 합니다.
    def test_persist_state_reports_save_error(self):
        console_interface = DummyConsoleInterface()
        game = self.make_game(
            state_repository=FailingSaveStateRepository(),
            console_interface_override=console_interface,
        )

        game.persist_state()

        self.assertTrue(console_interface.errors)

    # 저장 파일이 없으면 게임 상태를 기본값으로 준비해야 합니다.
    def test_initialize_state_uses_defaults_when_file_missing(self):
        console_interface = DummyConsoleInterface()
        game = self.make_game(
            state_repository=MissingStateRepository(),
            console_interface_override=console_interface,
        )

        game.initialize_state()

        self.assertGreaterEqual(len(game.runtime_state.quiz_catalog), 5)
        self.assertIsNone(game.runtime_state.game_lifecycle.record_book.best_score)
        self.assertEqual(list(game.runtime_state.game_lifecycle.record_book.history), [])
        self.assertTrue(console_interface.messages)

    # 저장 파일이 잘못되면 오류를 표시하고 복구해야 합니다.
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
            game = QuizGame(console_interface, StateRepository(state_file))

            game.initialize_state()

            backup_file = Path(temp_dir) / "state.json.bak"
            self.assertTrue(backup_file.exists())
            self.assertEqual(
                backup_file.read_text(encoding="utf-8"),
                broken_text,
            )
            restored_state = StateRepository(state_file).load_state()
            self.assertGreaterEqual(len(restored_state["quizzes"]), 5)
            self.assertTrue(console_interface.errors)

    def test_run_persists_partial_result_when_session_is_interrupted(self):
        console_interface = PlayMenuOnceConsoleInterface()
        repository = DummyStateRepository()
        factory = QuizFactory()
        repository.loaded_state = {
            "quizzes": [
                factory.create("문제1", ["A", "B", "C", "D"], 1),
                factory.create("문제2", ["A", "B", "C", "D"], 2),
            ],
            "best_score": None,
            "history": [],
        }
        game = self.make_game(
            state_repository=repository,
            console_interface_override=console_interface,
        )
        game.quiz_game_runner.quiz_game_execution.menu_action_dispatcher.menu_execution.quiz_play_workflow.quiz_session_service = InterruptedSessionService(
            QuizSessionResult(
                total_questions=QuestionCount(2),
                correct_count=CorrectAnswerCount(1),
                hint_used_count=HintUsageCount(0),
            )
        )

        game.run()

        self.assertIsNotNone(repository.saved)
        assert repository.saved is not None
        self.assertEqual(repository.saved["best_score"], 10)
        self.assertEqual(len(repository.saved["history"]), 1)
        self.assertEqual(repository.saved["history"][0]["correct_count"], 1)
        self.assertIn(constants.MESSAGE_INTERRUPTED_EXIT, console_interface.messages)


if __name__ == "__main__":
    unittest.main()
