import random
from dataclasses import dataclass
from typing import Optional

import app.config.constants as c
from app.model.quiz import Quiz
from app.ui.console_ui import ConsoleUI


# 한 번의 퀴즈 플레이 결과를 묶어서 저장하는 데이터입니다.
@dataclass(frozen=True)
class QuizSessionResult:
    total_questions: int
    correct_count: int
    hint_used_count: int


class QuizSessionInterrupted(Exception):
    def __init__(self, partial_result: Optional[QuizSessionResult] = None) -> None:
        super().__init__("quiz session interrupted")
        self.partial_result = partial_result


# 퀴즈를 실제로 진행하는 서비스입니다.
class QuizSessionService:
    def __init__(self, ui: ConsoleUI) -> None:
        self.ui = ui

    # 퀴즈 플레이 한 번을 끝까지 진행하고 결과를 돌려줍니다.
    def play(self, quizzes: list[Quiz]) -> Optional[QuizSessionResult]:
        if not quizzes:
            self.ui.show_message(c.MESSAGE_NO_QUIZZES)
            return None

        # 문제 수를 고르고, 그 수만큼 랜덤으로 출제합니다.
        question_count = self.choose_question_count(len(quizzes))
        selected_quizzes = self._select_quizzes(quizzes, question_count)
        correct_count = c.INITIAL_CORRECT_COUNT
        hint_used_count = c.INITIAL_HINT_USED_COUNT
        answered_question_count = c.INITIAL_CORRECT_COUNT

        try:
            # 바깥 for문은 "문제 단위" 반복이고,
            # 안쪽 while문은 "한 문제 안에서 올바른 입력이 들어올 때까지" 반복입니다.
            for index, quiz in enumerate(selected_quizzes, start=c.DISPLAY_INDEX_START):
                self.ui.show_question(quiz, index, len(selected_quizzes))
                used_hint_for_question = False

                while True:
                    # 정답 번호 또는 힌트 명령을 입력받습니다.
                    user_input = self.ui.get_answer_or_hint(
                        c.PROMPT_ANSWER,
                        c.MIN_ANSWER,
                        c.MAX_ANSWER,
                    )

                    if user_input == c.HINT_COMMAND_VALUE:
                        # 힌트가 없거나 이미 썼으면 다시 입력받습니다.
                        if not quiz.has_hint():
                            self.ui.show_error(c.ERROR_NO_HINT_FOR_QUESTION)
                            continue
                        if used_hint_for_question:
                            self.ui.show_error(c.ERROR_HINT_ALREADY_USED)
                            continue

                        # 힌트를 보여주고 감점 횟수를 올립니다.
                        self.ui.show_message(
                            c.MESSAGE_HINT_TEMPLATE.format(hint=quiz.get_hint_text())
                        )
                        used_hint_for_question = True
                        hint_used_count += 1
                        # 힌트를 본 뒤에도 바로 정답을 맞힌 것은 아니므로
                        # 같은 문제에서 다시 답을 입력받아야 합니다.
                        continue

                    # 숫자를 입력한 경우 정답 여부를 확인합니다.
                    if quiz.is_correct(user_input):
                        correct_count += 1
                        self.ui.show_message(c.MESSAGE_CORRECT_ANSWER)
                    else:
                        correct_text = quiz.choices[quiz.answer - c.DISPLAY_INDEX_START]
                        self.ui.show_error(
                            c.ERROR_WRONG_ANSWER_TEMPLATE.format(
                                answer=quiz.answer,
                                correct_text=correct_text,
                            )
                        )
                    answered_question_count += 1
                    # 정답이든 오답이든 숫자 답변까지 끝났으면
                    # 현재 문제 반복을 종료하고 다음 문제로 넘어갑니다.
                    break
        except (KeyboardInterrupt, EOFError) as exc:
            raise QuizSessionInterrupted(
                self._build_partial_result(
                    selected_quizzes,
                    correct_count,
                    hint_used_count,
                    answered_question_count,
                )
            ) from exc

        # 최종 반환값 하나에 필요한 결과를 모두 묶어 두면
        # QuizGame 쪽에서 값 여러 개를 따로 계산하지 않아도 됩니다.
        return QuizSessionResult(
            total_questions=len(selected_quizzes),
            correct_count=correct_count,
            hint_used_count=hint_used_count,
        )

    # 몇 문제를 풀지 입력받습니다.
    def choose_question_count(self, total_questions: int) -> int:
        return self.ui.get_valid_number(
            c.PROMPT_QUESTION_COUNT_TEMPLATE.format(count=total_questions),
            c.DISPLAY_INDEX_START,
            total_questions,
        )

    # 퀴즈 목록을 섞은 뒤 원하는 개수만큼 잘라서 반환합니다.
    def _select_quizzes(self, quizzes: list[Quiz], question_count: int) -> list[Quiz]:
        # 원본 self.quizzes 순서를 바꾸지 않으려고 복사본을 만든 뒤 섞습니다.
        working_quizzes = list(quizzes)
        random.shuffle(working_quizzes)
        return working_quizzes[:question_count]

    def _build_partial_result(
        self,
        selected_quizzes: list[Quiz],
        correct_count: int,
        hint_used_count: int,
        answered_question_count: int,
    ) -> Optional[QuizSessionResult]:
        if answered_question_count < c.DISPLAY_INDEX_START:
            return None

        return QuizSessionResult(
            total_questions=len(selected_quizzes),
            correct_count=correct_count,
            hint_used_count=hint_used_count,
        )
