# Mission 2 Quiz Game

Python 콘솔 환경에서 동작하는 퀴즈 게임입니다.  
현재 구조는 `state.json` 기반 영속성, 단일책임원칙(SRP), 객체지향 생활 체조 9원칙, 그리고 책임이 드러나는 패키지 경계를 함께 맞추는 방향으로 정리되어 있습니다.

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
pyright /Users/ilim/Downloads/week2/cs_2
```

## 현재 구조

```text
app/
├── __init__.py
├── application/
│   ├── __init__.py
│   ├── menu_action_dispatcher.py
│   ├── menu_execution.py
│   ├── quiz_game.py
│   ├── quiz_game_execution.py
│   ├── quiz_game_runner.py
│   ├── catalog/
│   │   ├── __init__.py
│   │   ├── quiz_catalog_creation_service.py
│   │   ├── quiz_catalog_deletion_service.py
│   │   ├── quiz_catalog_listing_service.py
│   │   └── quiz_catalog_mutation_workflow.py
│   ├── play/
│   │   ├── __init__.py
│   │   ├── best_score_service.py
│   │   ├── question_count_chooser.py
│   │   ├── quiz_history_service.py
│   │   ├── quiz_partial_result_builder.py
│   │   ├── quiz_play_result_handler.py
│   │   ├── quiz_play_workflow.py
│   │   ├── quiz_question_round_service.py
│   │   ├── quiz_result_recorder.py
│   │   ├── quiz_round_coordinator.py
│   │   ├── quiz_score_keeper.py
│   │   ├── quiz_scoring_service.py
│   │   ├── quiz_session_models.py
│   │   └── quiz_session_service.py
│   └── state/
│       ├── __init__.py
│       ├── default_game_state_factory.py
│       ├── default_state_recovery.py
│       ├── game_bootstrap_service.py
│       ├── game_exit_persistence.py
│       ├── game_history.py
│       ├── game_lifecycle.py
│       ├── game_persistence_service.py
│       ├── game_record_book.py
│       ├── game_runtime_state.py
│       ├── game_shutdown_service.py
│       └── game_state_service.py
├── config/
│   ├── __init__.py
│   └── constants.py
├── console/
│   ├── __init__.py
│   ├── input.py
│   ├── interface.py
│   └── output.py
├── model/
│   ├── __init__.py
│   ├── quiz.py
│   ├── quiz_catalog.py
│   ├── quiz_components.py
│   └── quiz_factory.py
├── presentation/
│   ├── __init__.py
│   ├── best_score_display_service.py
│   └── quiz_presenter.py
├── repository/
│   ├── __init__.py
│   ├── quiz_payload_mapper.py
│   ├── state_payload_mapper.py
│   └── state_repository.py
└── service/
    ├── __init__.py
    └── quiz_metrics.py
```

## 패키지별 역할

### `app/console`

- 콘솔 입출력 경계
- `input.py`: 숫자, 문자열, yes/no, 정답/힌트 입력 검증
- `output.py`: 메뉴, 문제, 결과, 목록, 오류 메시지 출력
- `interface.py`: 입력/출력을 묶는 얇은 facade

### `app/application`

- 애플리케이션 흐름과 orchestration
- 패키지 기준으로 "왜 변경되는가"가 드러나도록 나눈 계층

#### `app/application/catalog`

- 퀴즈 추가, 삭제, 목록 보기 흐름
- 카탈로그 mutation과 listing 책임 분리

#### `app/application/play`

- 퀴즈 플레이 세션, 라운드, 점수 계산, 결과 기록
- 문제 수 선택, 점수 정책, 최고 점수 갱신, history 기록

#### `app/application/state`

- 런타임 상태, 부트스트랩, 기본 상태 복구, 저장, 종료
- `state.json`과 맞닿는 애플리케이션 상태 흐름

#### `app/application` 루트

- `QuizGame`: composition root
- `QuizGameExecution`, `QuizGameRunner`: 실행 루프와 진입점 분리
- `MenuActionDispatcher`, `MenuExecution`: 메뉴 선택과 실제 동작 위임 분리

### `app/model`

- 도메인 모델
- `Quiz`: 문제 한 개의 핵심 행위 중심 객체
- `QuizPrompt`, `QuizSolution`, `QuestionText`, `ChoiceSet`, `AnswerNumber`, `HintText`
  : 퀴즈 입력 규칙과 값 의미를 가진 값 객체
- `QuizCatalog`: 퀴즈 컬렉션 전용 일급 컬렉션
- `QuizFactory`: 검증된 값 객체를 조합해 `Quiz` 생성

### `app/presentation`

- 콘솔에 보여줄 표현 로직
- `QuizPresenter`: 문제/목록/오답/힌트 표현 전용
- `BestScoreDisplayService`: 최고 점수 표시 책임 분리

### `app/repository`

- 파일 입출력과 payload 변환 경계
- `StateRepository`: `state.json` 파일 읽기/쓰기
- `StatePayloadMapper`: 전체 상태 스키마 검증/복원
- `QuizPayloadMapper`: `Quiz` <-> payload 변환

### `app/service`

- 여러 패키지에서 공통으로 쓰는 shared value objects
- 현재는 `quiz_metrics.py`만 두고, 나머지 orchestration/service 성격 코드는 `app/application`과 `app/presentation`으로 이동

## 설계 방향

현재 구조는 다음 기준으로 정리되어 있습니다.

- SRP: 한 클래스는 하나의 이유로만 변경
- 객체지향 생활 체조 9원칙 준수
- 패키지 구조도 실제 책임 경계를 반영
- 점수/질문 수/표시 인덱스/메뉴 선택/타임스탬프 같은 값을 wrapper 객체로 승격
- 직접 리스트 조작 대신 일급 컬렉션 사용
- 실행 흐름, 저장, 복구, 점수 정책, 콘솔 입출력, 표현 책임 분리

## 주요 리팩터링 포인트

- 기존 top-level 콘솔 모듈을 `app/console` 패키지로 승격
- flat한 `app/service` 디렉터리를 `application/catalog`, `application/play`, `application/state`, `presentation` 기준으로 재구성
- `Quiz` 엔티티에서 payload/presentation 성격을 분리하고 mapper/presenter로 이동
- `GameRuntimeState`에서 bootstrap/save/display helper를 걷어내고 상태 객체 역할에 더 집중
- 카탈로그 mutation, listing, persistence 연결을 별도 클래스로 분리
- 의미 있는 chained access와 제어흐름 중첩을 줄여 strict audit 통과

## 엔트리 포인트

- 프로그램 시작: [main.py](/Users/ilim/Downloads/week2/cs_2/main.py)
- composition root: [quiz_game.py](/Users/ilim/Downloads/week2/cs_2/app/application/quiz_game.py)
- 콘솔 facade: [interface.py](/Users/ilim/Downloads/week2/cs_2/app/console/interface.py)

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
