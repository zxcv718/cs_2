import app.config.constants as c
from app.model.quiz import Quiz
from app.repository.state_repository import StateRepository
from app.service.game_state_service import GameStateService
from app.service.quiz_catalog_service import QuizCatalogService
from app.service.quiz_session_service import QuizSessionService
from app.ui.console_ui import ConsoleUI
from typing import Any, Optional


# 전체 프로그램 흐름을 조율하는 메인 서비스입니다.
class QuizGame:
    def __init__(self, ui: ConsoleUI, state_repository: StateRepository) -> None:
        self.ui = ui
        self.state_repository = state_repository
        # 책임을 나눈 하위 서비스들을 함께 사용합니다.
        self.state_service = GameStateService(ui, state_repository)
        self.catalog_service = QuizCatalogService(ui)
        self.session_service = QuizSessionService(ui)
        self.quizzes: list[Quiz] = []
        self.best_score: Optional[int] = None
        self.history: list[dict[str, Any]] = []
        self._initialized = False

    # 저장 파일에서 상태를 읽어 게임 메모리에 올립니다.
    def initialize_state(self) -> None:
        # 실제 파일 읽기와 예외 복구는 state_service가 담당하고,
        # QuizGame은 그 결과를 현재 메모리 상태에 반영만 합니다.
        state = self.state_service.load_or_initialize_state()
        self.quizzes = state[c.STATE_KEY_QUIZZES]
        self.best_score = state[c.STATE_KEY_BEST_SCORE]
        self.history = state.get(c.STATE_KEY_HISTORY, [])
        self._initialized = True

    # 현재 메모리 상태를 파일에 저장합니다.
    def persist_state(self) -> None:
        self.state_service.save_state(self.quizzes, self.best_score, self.history)

    # 메뉴를 반복해서 보여주며 사용자의 선택에 맞는 기능을 실행합니다.
    def run(self) -> None:
        if not self._initialized:
            self.initialize_state()

        has_delete = c.ENABLE_DELETE_MENU
        max_choice = c.MENU_MAX_CHOICE_WITH_DELETE if has_delete else c.MENU_MAX_CHOICE_WITHOUT_DELETE

        while True:
            try:
                self.ui.show_menu(has_delete=has_delete)
                choice = self.ui.get_menu_choice(c.MENU_MIN_CHOICE, max_choice)

                # 메뉴 번호를 직접 비교해 분기하면
                # "입력 -> 기능 실행 -> 다시 메뉴로 복귀" 흐름이 한눈에 보입니다.
                if choice == c.MENU_PLAY:
                    self.play_quiz()
                elif choice == c.MENU_ADD:
                    self.add_quiz()
                elif choice == c.MENU_LIST:
                    self.list_quizzes()
                elif has_delete and choice == c.MENU_DELETE:
                    self.delete_quiz()
                elif (has_delete and choice == c.MENU_SCORE) or (not has_delete and choice == c.MENU_DELETE):
                    self.show_best_score()
                elif (has_delete and choice == c.MENU_EXIT) or (not has_delete and choice == c.MENU_SCORE):
                    self.persist_state()
                    self.ui.show_message(c.MESSAGE_PROGRAM_EXIT)
                    break
            except (KeyboardInterrupt, EOFError):
                # 강제 종료가 들어와도 저장 후 안전하게 끝냅니다.
                self.ui.show_message(c.MESSAGE_INTERRUPTED_EXIT)
                self.persist_state()
                break

    # 퀴즈 플레이를 실행하고 결과를 최고 점수와 기록에 반영합니다.
    def play_quiz(self) -> None:
        # 실제 문제 출제와 채점은 session_service에 맡기고,
        # 여기서는 결과를 받아 최고 점수와 history를 갱신합니다.
        result = self.session_service.play(self.quizzes)
        if result is None:
            return

        # 최고 점수 갱신 여부를 함께 받아서
        # 결과 화면 뒤에 "최고 점수 갱신" 메시지를 보여줄 수 있게 합니다.
        self.best_score, is_new_record = self.session_service.update_best_score(
            self.best_score,
            result.score,
        )
        # history에는 플레이 결과를 딕셔너리 한 건으로 쌓아 둡니다.
        # 이렇게 하면 나중에 JSON으로 저장하기 쉽습니다.
        self.history.append(self.session_service.create_history_entry(result))
        self.persist_state()
        self.ui.show_result(
            result.correct_count,
            result.score,
            result.total_questions,
            result.hint_used_count,
        )
        if is_new_record:
            self.ui.show_message(c.MESSAGE_BEST_SCORE_UPDATED)

    # 새 퀴즈를 추가한 뒤 바로 저장합니다.
    def add_quiz(self) -> None:
        if self.catalog_service.add_quiz(self.quizzes):
            self.persist_state()

    # 현재 퀴즈 목록을 화면에 출력합니다.
    def list_quizzes(self) -> None:
        self.catalog_service.list_quizzes(self.quizzes)

    # 최고 점수만 따로 확인할 수 있게 보여줍니다.
    def show_best_score(self) -> None:
        self.ui.show_best_score(self.best_score)

    # 퀴즈를 삭제한 경우에만 저장합니다.
    def delete_quiz(self) -> None:
        if self.catalog_service.delete_quiz(self.quizzes):
            self.persist_state()
