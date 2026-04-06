# Mission 2 Quiz Game

Python 콘솔 환경에서 동작하는 퀴즈 게임입니다.  
현재 구조는 `state.json` 기반 영속성, 계층 분리, 단일책임원칙, 그리고 객체지향 생활 체조 9원칙을 함께 맞추는 방향으로 리팩터링되어 있습니다.

## 핵심 기능

- 콘솔 메뉴로 퀴즈 풀기, 추가, 목록 확인, 삭제, 최고 점수 확인
- `state.json` 기반 퀴즈/최고 점수/플레이 기록 유지
- 퀴즈 진행 중 인터럽트 발생 시 부분 결과를 가능한 범위에서 저장
- `pytest`, `unittest`, `pyright` 기준 green 유지

## 실행

```bash
python3 main.py
```

## 검증

```bash
python3 -m pytest -q
python3 -m unittest -q
pyright /Users/ilim/Downloads/week2/cs_2 --outputjson
```

## 현재 구조

```text
app/
├── __init__.py
├── console_interface.py
├── config/
│   ├── __init__.py
│   └── constants.py
├── model/
│   ├── __init__.py
│   ├── quiz.py
│   ├── quiz_catalog.py
│   ├── quiz_components.py
│   └── quiz_factory.py
├── repository/
│   ├── __init__.py
│   ├── quiz_payload_mapper.py
│   ├── state_payload_mapper.py
│   └── state_repository.py
└── service/
    ├── __init__.py
    ├── best_score_service.py
    ├── default_game_state_factory.py
    ├── default_state_recovery.py
    ├── game_bootstrap_service.py
    ├── game_exit_persistence.py
    ├── game_history.py
    ├── game_lifecycle.py
    ├── game_persistence_service.py
    ├── game_record_book.py
    ├── game_runtime_state.py
    ├── game_shutdown_service.py
    ├── game_state_service.py
    ├── menu_action_dispatcher.py
    ├── menu_execution.py
    ├── quiz_catalog_service.py
    ├── quiz_catalog_workflow.py
    ├── quiz_game.py
    ├── quiz_game_execution.py
    ├── quiz_game_runner.py
    ├── quiz_history_service.py
    ├── quiz_metrics.py
    ├── quiz_partial_result_builder.py
    ├── quiz_play_result_handler.py
    ├── quiz_play_workflow.py
    ├── quiz_question_round_service.py
    ├── quiz_result_recorder.py
    ├── quiz_round_coordinator.py
    ├── quiz_score_keeper.py
    ├── quiz_scoring_service.py
    ├── quiz_selection_service.py
    ├── quiz_session_models.py
    └── quiz_session_service.py
```

## 계층별 역할

### `app/config`

- 전역 상수와 파일/메뉴/메시지 정의

### `app/model`

- `Quiz`: 문제 한 개의 행위 중심 도메인 객체
- `QuizPrompt`, `QuizSolution`, `QuestionText`, `ChoiceSet`, `AnswerNumber`, `HintText`
  : 퀴즈 입력 규칙과 출력/검증 책임을 분리한 값 객체
- `QuizCatalog`: 퀴즈 컬렉션 전용 일급 컬렉션
- `QuizFactory`: 검증된 값 객체를 조합해 `Quiz` 생성

### `app/repository`

- `StateRepository`: `state.json` 파일 입출력 경계
- `StatePayloadMapper`: 상태 스키마 검증/복원
- `QuizPayloadMapper`: `Quiz` <-> payload 변환

### `app/service`

- `QuizGame`: composition root
- `QuizGameRunner`, `QuizGameExecution`, `MenuActionDispatcher`, `MenuExecution`
  : 실행 흐름과 메뉴 디스패치 분리
- `QuizSessionService`, `QuizRoundCoordinator`, `QuizQuestionRoundService`
  : 세션/라운드 진행 책임 분리
- `QuizCatalogService`, `QuizCatalogWorkflow`
  : 퀴즈 추가/삭제/목록 흐름 분리
- `QuizScoringService`, `BestScoreService`, `QuizScoreKeeper`, `QuizResultRecorder`
  : 점수 계산/최고 점수/결과 기록 책임 분리
- `GameRuntimeState`, `GameRecordBook`, `GameHistory`, `GameLifecycle`
  : 런타임 상태와 기록 책임 분리
- `GameBootstrapService`, `DefaultStateRecovery`, `GamePersistenceService`, `GameExitPersistence`, `GameShutdownService`
  : 로딩/복구/저장/종료 책임 분리
- `QuizSessionResult`, `QuizQuestionRoundResult` 등 세션 모델 분리
- `QuestionCount`, `CorrectAnswerCount`, `HintUsageCount`, `ScoreValue`, `MenuChoice`, `DisplayIndex`, `PlayedAt`
  : 원시값을 감싼 메트릭/식별 값 객체

### `app/console_interface.py`

- 콘솔 입출력 경계
- 메뉴 입력, 숫자 입력, yes/no 입력, 정답/힌트 입력, 결과 출력

## 설계 방향

현재 구조는 다음 목표를 기준으로 정리되었습니다.

- 단일책임원칙: 한 클래스는 하나의 이유로만 변경
- 객체지향 생활 체조 9원칙 준수
- 점수/질문 수/표시 인덱스/메뉴 선택/타임스탬프 같은 값을 wrapper 객체로 승격
- 직접 리스트 조작 대신 일급 컬렉션 사용
- 실행 흐름, 저장, 복구, 점수 정책, 콘솔 입출력 책임 분리

## 주요 리팩터링 포인트

- 기존 `app/ui/console_ui.py` 경계를 [console_interface.py](/Users/ilim/Downloads/week2/cs_2/app/console_interface.py)로 승격
- `QuizGame`이 모든 걸 직접 하던 구조에서 조립과 실행 책임을 분리
- 세션/라운드/결과 기록/카탈로그/저장/복구를 작은 서비스로 분할
- 메뉴 번호, 점수, 질문 수, 힌트 사용 수, 표시 인덱스, 플레이 시간에 대해 wrapper 도입
- 의미 있는 chained access와 제어흐름 중첩을 줄여 strict audit 통과

## 데이터 파일

- 저장 파일: `state.json`
- 저장 내용:
  - 퀴즈 목록
  - 최고 점수
  - 플레이 히스토리

예시 스키마:

```json
{
  "quizzes": [
    {
      "question": "Python의 창시자는?",
      "choices": ["Guido", "Linus", "Bjarne", "James"],
      "answer": 1,
      "hint": "Guido로 시작합니다."
    }
  ],
  "best_score": 26,
  "history": [
    {
      "played_at": "2026-04-03T19:11:39",
      "total_questions": 5,
      "correct_count": 4,
      "score": 38,
      "hint_used_count": 1
    }
  ]
}
```

## 테스트 파일

- [test_quiz.py](/Users/ilim/Downloads/week2/cs_2/tests/test_quiz.py)
- [test_state_repository.py](/Users/ilim/Downloads/week2/cs_2/tests/test_state_repository.py)
- [test_quiz_game.py](/Users/ilim/Downloads/week2/cs_2/tests/test_quiz_game.py)

이 테스트들은 도메인 규칙, 저장소 스키마, 세션/런타임 흐름을 보호합니다.

## 최근 리팩터링 커밋

```text
55f04b2 Tighten metric wrappers to close the remaining calisthenics gaps
a0f68bc Finish the calisthenics cleanup under the current Python design
25c9eb3 Move console boundary and keep the refactor green
520f10b Wrap core quiz metrics and remove remaining control-flow shortcuts
2161b03 Push domain wrappers and menu flow toward calisthenics compliance
27ce941 Reduce coordinator state while preserving quiz behavior
```
