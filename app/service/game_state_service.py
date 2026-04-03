from typing import Any, Optional

import app.config.constants as c
from app.model.quiz import Quiz
from app.repository.state_repository import StateRepository
from app.ui.console_ui import ConsoleUI


# 게임 상태를 불러오고 저장하는 역할만 맡는 서비스입니다.
class GameStateService:
    def __init__(self, ui: ConsoleUI, state_repository: StateRepository) -> None:
        self.ui = ui
        self.state_repository = state_repository

    # 코드에 들어 있는 기본 퀴즈 데이터를 Quiz 객체로 만듭니다.
    def create_default_quizzes(self) -> list[Quiz]:
        return [
            Quiz(
                item[c.QUIZ_FIELD_QUESTION],
                list(item[c.QUIZ_FIELD_CHOICES]),
                item[c.QUIZ_FIELD_ANSWER],
                hint=item.get(c.QUIZ_FIELD_HINT),
            )
            for item in c.DEFAULT_QUIZ_DATA
        ]

    # 파일 상태를 읽고, 문제가 있으면 기본 상태로 복구합니다.
    def load_or_initialize_state(self) -> dict[str, Any]:
        try:
            return self.state_repository.load_state()
        except FileNotFoundError:
            # 파일이 없으면 기본 데이터로 새로 시작합니다.
            self.ui.show_message(c.MESSAGE_STATE_FILE_MISSING)
            state = self._build_default_state()
            self.save_state(
                state[c.STATE_KEY_QUIZZES],
                state[c.STATE_KEY_BEST_SCORE],
                state[c.STATE_KEY_HISTORY],
            )
            return state
        except ValueError:
            # 파일 내용이 잘못되면 오류를 알리고 기본 데이터로 복구합니다.
            self.ui.show_error(c.ERROR_STATE_CORRUPTED)
            state = self._build_default_state()
            self.save_state(
                state[c.STATE_KEY_QUIZZES],
                state[c.STATE_KEY_BEST_SCORE],
                state[c.STATE_KEY_HISTORY],
            )
            return state
        except OSError:
            # 읽기 자체가 실패하면 저장은 건너뛰고 기본 상태만 돌려줍니다.
            self.ui.show_error(c.ERROR_STATE_READ)
            return self._build_default_state()

    # 현재 상태를 저장소에 저장합니다.
    def save_state(
        self,
        quizzes: list[Quiz],
        best_score: Optional[int],
        history: list[dict[str, Any]],
    ) -> None:
        try:
            self.state_repository.save_state(quizzes, best_score, history)
        except OSError:
            self.ui.show_error(c.ERROR_STATE_SAVE)

    # 기본 상태는 기본 퀴즈, 최고 점수 없음, 빈 기록으로 구성됩니다.
    def _build_default_state(self) -> dict[str, Any]:
        return {
            c.STATE_KEY_QUIZZES: self.create_default_quizzes(),
            c.STATE_KEY_BEST_SCORE: None,
            c.STATE_KEY_HISTORY: [],
        }
