# Mission 2 Quiz Game

Python 콘솔 환경에서 동작하는 퀴즈 게임입니다.  
현재 구조는 `state.json` 기반 영속성, 단일책임원칙(SRP), 객체지향 생활 체조 9원칙, 그리고 책임이 드러나는 패키지 경계를 함께 맞추는 방향으로 정리되어 있습니다.  
최근에는 `rule 6`과 `rule 9` 쪽 잔여 지점을 줄이기 위해 콘솔/저장소 계층을 더 작은 역할 객체로 분해했고, `app/`는 `__init__.py` 없는 namespace package 형태로 정리했습니다.

## 퀴즈 주제와 선정 이유

- 퀴즈 주제는 `Python 기초 문법과 프로그래밍 기본 개념`입니다.
- 기본 퀴즈에는 Python의 창시자, 리스트 기호, 함수 정의 키워드, 조건 분기 키워드, 반복문 탈출 키워드처럼 Python 입문 과정에서 바로 만나는 내용이 들어 있습니다.
- 이 주제를 고른 이유는 이번 미션 자체가 Python으로 프로그램을 구현하는 과제이기 때문입니다.
- 즉 프로그램을 만드는 과정과 퀴즈의 내용이 서로 연결되도록 해서, 단순히 기능만 구현하는 것이 아니라 Python 기초 개념도 함께 복습할 수 있게 했습니다.

## 핵심 기능

- 콘솔 메뉴로 퀴즈 풀기, 추가, 목록 확인, 삭제, 최고 점수 확인
- `state.json` 기반 퀴즈/최고 점수/플레이 기록 유지
- 손상된 `state.json`을 가능한 경우 `.bak`로 보존한 뒤 기본 상태로 복구
- 임시 파일 저장 후 교체하는 방식으로 상태 파일을 atomic 하게 저장
- 퀴즈 진행 중 인터럽트 발생 시 부분 결과를 가능한 범위에서 저장
- `pytest`, `unittest`, `pyright`와 구조 규칙 테스트 기준 green 유지

## 실행

```bash
python3 main.py
```

## 검증

```bash
python3 -m pytest -q tests/test_architecture.py
python3 -m pytest -q
python3 -m unittest -q
pyright /Users/ilim/Downloads/week2/cs_2
```

## 스크린샷

### 개발 환경

현재 개발 환경에서 Python과 Git 버전을 확인한 화면입니다.

![개발 환경 스크린샷](env.png)

### 프로그램 실행 결과

메뉴 출력, 점수 확인, 퀴즈 추가 입력 흐름, 퀴즈 플레이 흐름 일부를 확인할 수 있는 실행 스크린샷입니다.

![프로그램 실행 결과 스크린샷](result.png)

### Git 로그

`git log --oneline --graph` 결과 스크린샷입니다. 브랜치 병합 이력과 커밋 흐름을 확인할 수 있습니다.

![Git 로그 스크린샷](gitlog.png)

## 현재 구조

```text
app/
├── application/
│   ├── menu_action_dispatcher.py
│   ├── menu_execution.py
│   ├── quiz_game.py
│   ├── quiz_game_execution.py
│   ├── quiz_game_factory.py
│   ├── quiz_game_runner.py
│   ├── catalog/
│   │   ├── quiz_catalog_creation_service.py
│   │   ├── quiz_catalog_deletion_service.py
│   │   └── quiz_catalog_listing_service.py
│   ├── play/
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
│       ├── default_game_state_factory.py
│       ├── default_state_recovery.py
│       ├── game_bootstrap_service.py
│       ├── game_exit_persistence.py
│       ├── game_history.py
│       ├── game_persistence_service.py
│       ├── game_record_book.py
│       ├── game_runtime_state.py
│       ├── game_shutdown_service.py
│       ├── game_snapshot.py
│       ├── game_state_service.py
│       └── quiz_history_entry.py
├── config/
│   └── constants.py
├── console/
│   ├── input.py
│   ├── interface.py
│   └── output.py
├── model/
│   ├── quiz.py
│   ├── quiz_catalog.py
│   ├── quiz_components.py
│   ├── quiz_factory.py
│   └── quiz_selection.py
├── presentation/
│   ├── best_score_display_service.py
│   └── quiz_presenter.py
├── repository/
│   ├── quiz_payload_mapper.py
│   ├── state_payload_mapper.py
│   └── state_repository.py
└── service/
    └── quiz_metrics.py
```

## 패키지별 역할

### `app/console`

- 콘솔 입출력 경계
- `input.py`: `ConsoleInput` facade와 숫자/문자열/yes-no/정답-또는-힌트 입력 역할 객체
- `output.py`: 메뉴, 메시지, 목록, 문제, 결과 출력 책임을 더 작은 출력 역할 객체로 분리
- `interface.py`: `ConsoleReader`, `ConsoleWriter`를 합친 얇은 facade

### `app/application`

- 애플리케이션 흐름과 orchestration
- 패키지 기준으로 "왜 변경되는가"가 드러나도록 나눈 계층

#### `app/application/catalog`

- 퀴즈 추가, 삭제, 목록 보기 유스케이스
- add/delete/list를 별도 action에서 조합할 수 있게 분리

#### `app/application/play`

- 퀴즈 플레이 세션, 라운드, 점수 계산, 결과 기록
- 문제 수 선택, 점수 정책, 최고 점수 갱신, history 기록

#### `app/application/state`

- 런타임 상태, snapshot, history entry, 기본 상태 복구, 저장, 종료
- 손상된 상태 파일 백업 후 기본 상태 복구, 인터럽트 종료 저장
- `state.json`과 맞닿는 애플리케이션 상태 흐름

#### `app/application` 루트

- `QuizGame`: 런타임 상태와 runner를 감싸는 facade
- `QuizGameFactory`: object graph 조립 전담 composition root
- `QuizGameExecution`, `QuizGameRunner`: 실행 루프와 진입점 분리
- `MenuActionDispatcher`, `MenuActions`: 메뉴 선택과 action dispatch 분리

### `app/model`

- 도메인 모델
- `Quiz`: 문제 한 개의 핵심 행위 중심 객체
- `QuizPrompt`, `QuizSolution`, `QuestionText`, `ChoiceSet`, `AnswerNumber`, `HintText`
  : 퀴즈 입력 규칙과 값 의미를 가진 값 객체
- `QuizCatalog`: 퀴즈 컬렉션 전용 일급 컬렉션
- `QuizSelection`: 플레이 대상으로 뽑힌 퀴즈 집합 전용 일급 컬렉션
- `QuizFactory`: 검증된 값 객체를 조합해 `Quiz` 생성

### `app/presentation`

- 콘솔에 보여줄 표현 로직
- `QuizPresenter`: 문제/목록/오답/힌트 표현 전용
- `BestScoreDisplayService`: 최고 점수 표시 책임 분리

### `app/repository`

- 파일 입출력과 payload 변환 경계
- `StateRepository`: `GameSnapshot` <-> `state.json` 읽기/쓰기, atomic 저장, 손상 파일 백업 지원
  - 내부적으로 loader / writer / backup helper를 분리
- `StatePayloadMapper`: `GameSnapshot` 기준 전체 상태 스키마 검증/복원
  - 내부적으로 reader / writer / history translator 역할로 분리
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
- runtime state와 history를 raw `dict` 대신 snapshot/value object로 다룸
- 구조 규칙을 테스트로 고정
- repo-local strict 기준으로 `rule 6`을 메서드 수 상한으로 운영하고, `rule 9`는 public direct-field-return 금지로 고정
- 실행 흐름, 저장, 복구, 점수 정책, 콘솔 입출력, 표현 책임 분리

## 구조 규칙 메모

- `app/`는 Python namespace package 형태로 사용하고 있어서 `app/**/__init__.py`는 두지 않습니다.
- 대신 `tests/__init__.py`는 `python3 -m unittest -q` discovery 호환을 위해 유지합니다.
- 구조 검사는 `tests/test_architecture.py` 에서 고정합니다.
- 현재 구조 테스트는 다음을 검사합니다.
  - `else` 금지
  - getter/setter/property 금지
  - public method의 direct field return 금지
  - 인스턴스 변수 2개 이하
  - production class 메서드 수 상한 `10`
  - raw `list/dict/Any` annotation 금지
  - runtime train-wreck 호출 금지

## 데이터 파일

- 저장 파일: `state.json`
- 저장 내용:
  - 퀴즈 목록
  - 최고 점수
  - 플레이 히스토리
- 손상된 상태 파일을 읽으면 가능한 경우 `state.json.bak`로 보존 후 기본 상태로 복구

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
