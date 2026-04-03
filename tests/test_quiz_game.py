import unittest

from app.model.quiz import Quiz
from app.service.best_score_service import BestScoreService
from app.service.default_game_state_factory import DefaultGameStateFactory
from app.service.game_state_service import GameStateService
from app.service.quiz_game import QuizGame
from app.service.quiz_history_service import QuizHistoryService
from app.service.quiz_scoring_service import QuizScoringService
from app.service.quiz_session_service import QuizSessionResult


# 실제 입력 대신 테스트에서 사용할 가짜 UI입니다.
class DummyUI:
    def __init__(self):
        self.messages = []
        self.errors = []

    # 출력된 일반 메시지를 리스트에 모읍니다.
    def show_message(self, message):
        self.messages.append(message)

    # 출력된 오류 메시지를 리스트에 모읍니다.
    def show_error(self, message):
        self.errors.append(message)


# 실제 파일 대신 메모리에 저장 결과를 남기는 가짜 저장소입니다.
class DummyStateRepository:
    def __init__(self):
        self.saved = None
        self.loaded_state = {
            "quizzes": [Quiz("기본 문제", ["A", "B", "C", "D"], 1)],
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

        best_score, is_new_record = service.update_best_score(None, 30)

        self.assertEqual(best_score, 30)
        self.assertTrue(is_new_record)

    # 더 높은 점수가 나오면 최고 점수가 바뀌어야 합니다.
    def test_update_best_score_replaces_lower_score(self):
        service = BestScoreService()

        best_score, is_new_record = service.update_best_score(20, 30)

        self.assertEqual(best_score, 30)
        self.assertTrue(is_new_record)

    # 더 낮은 점수는 최고 점수를 바꾸면 안 됩니다.
    def test_update_best_score_keeps_higher_score(self):
        service = BestScoreService()

        best_score, is_new_record = service.update_best_score(40, 30)

        self.assertEqual(best_score, 40)
        self.assertFalse(is_new_record)


# 점수 계산 규칙만 담당하는 서비스를 테스트합니다.
class QuizScoringServiceTestCase(unittest.TestCase):
    # 힌트를 쓰지 않으면 정답 수만큼 점수가 올라야 합니다.
    def test_calculate_score_without_hint(self):
        service = QuizScoringService()

        score = service.calculate_score(correct_count=4, hint_used_count=0)

        self.assertEqual(score, 40)

    # 힌트를 쓰면 감점이 반영되어야 합니다.
    def test_calculate_score_with_hint_penalty(self):
        service = QuizScoringService(hint_penalty=2)

        score = service.calculate_score(correct_count=4, hint_used_count=1)

        self.assertEqual(score, 38)

    # 감점이 커도 최종 점수는 0점 아래로 내려가면 안 됩니다.
    def test_calculate_score_never_goes_below_zero(self):
        service = QuizScoringService(hint_penalty=20)

        score = service.calculate_score(correct_count=1, hint_used_count=1)

        self.assertEqual(score, 0)


# 플레이 결과를 history 형식으로 바꾸는 서비스를 테스트합니다.
class QuizHistoryServiceTestCase(unittest.TestCase):
    # 플레이 결과가 history용 딕셔너리로 잘 바뀌는지 확인합니다.
    def test_create_entry_returns_expected_fields(self):
        service = QuizHistoryService()
        result = QuizSessionResult(
            total_questions=5,
            correct_count=4,
            hint_used_count=1,
        )

        item = service.create_entry(result, score=38)

        self.assertEqual(item["total_questions"], 5)
        self.assertEqual(item["correct_count"], 4)
        self.assertEqual(item["score"], 38)
        self.assertEqual(item["hint_used_count"], 1)
        self.assertIn("played_at", item)


# QuizGame이 하위 서비스를 제대로 호출하는지 테스트합니다.
class QuizGameTestCase(unittest.TestCase):
    # 기본 가짜 객체를 붙여 게임 객체를 쉽게 만듭니다.
    def make_game(self, state_repository=None, ui=None):
        return QuizGame(ui or DummyUI(), state_repository or DummyStateRepository())

    # persist_state가 저장소에 저장을 위임하는지 확인합니다.
    def test_persist_state_delegates_to_state_repository(self):
        game = self.make_game()
        game.quizzes = [Quiz("문제", ["A", "B", "C", "D"], 1)]
        game.best_score = 50
        game.history = []

        game.persist_state()

        self.assertIsNotNone(game.state_repository.saved)
        self.assertEqual(game.state_repository.saved["best_score"], 50)

    # 저장 실패 시 UI에 오류를 보여줘야 합니다.
    def test_persist_state_reports_save_error(self):
        ui = DummyUI()
        game = self.make_game(state_repository=FailingSaveStateRepository(), ui=ui)

        game.persist_state()

        self.assertTrue(ui.errors)

    # 저장 파일이 없으면 게임 상태를 기본값으로 준비해야 합니다.
    def test_initialize_state_uses_defaults_when_file_missing(self):
        ui = DummyUI()
        game = self.make_game(state_repository=MissingStateRepository(), ui=ui)

        game.initialize_state()

        self.assertGreaterEqual(len(game.quizzes), 5)
        self.assertIsNone(game.best_score)
        self.assertEqual(game.history, [])
        self.assertTrue(ui.messages)

    # 저장 파일이 잘못되면 오류를 표시하고 복구해야 합니다.
    def test_initialize_state_recovers_on_value_error(self):
        ui = DummyUI()
        game = self.make_game(state_repository=BrokenStateRepository(), ui=ui)

        game.initialize_state()

        self.assertGreaterEqual(len(game.quizzes), 5)
        self.assertTrue(ui.errors)


if __name__ == "__main__":
    unittest.main()
