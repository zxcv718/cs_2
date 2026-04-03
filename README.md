# Mission 2 Quiz Game

Python 콘솔 환경에서 동작하는 퀴즈 게임입니다. 객체지향 구조와 JSON 기반 데이터 영속성을 함께 연습하는 것이 목표입니다.

## 프로젝트 개요

- 콘솔 메뉴를 통해 퀴즈 풀기, 추가, 목록 조회, 삭제, 점수 확인을 수행합니다.
- 프로그램을 다시 실행해도 퀴즈와 최고 점수, 플레이 히스토리가 유지됩니다.

## 퀴즈 주제 선정 이유

- 주제는 `Python 기초`입니다.
- Mission 2의 학습 목표와 직접 연결되고, 기본 문법/키워드/자료형 문제를 만들기 쉽기 때문입니다.

## 실행 방법

```bash
python3 main.py
```

테스트 실행:

```bash
python3 -m unittest discover -s tests
```

## 기능 목록

- 메뉴 출력
- 퀴즈 풀기
- 퀴즈 추가
- 퀴즈 목록 확인
- 퀴즈 삭제
- 최고 점수 확인
- 랜덤 출제
- 문제 수 선택
- 힌트 사용 및 점수 차감
- 점수 기록 히스토리 저장
- 파일 없음 / 손상 복구
- 안전 종료 처리

## 사용 흐름 메모

- 첫 실행에서 `state.json`이 없으면 기본 퀴즈 데이터로 시작합니다.
- 실행 중 퀴즈를 추가하거나 삭제하면 변경 내용이 `state.json`에 저장됩니다.
- `Ctrl+C` 또는 입력 종료가 발생해도 가능한 범위에서 저장 후 종료하도록 처리합니다.
- clone/pull 실습 확인을 위해 2026-04-03에 README 검증 문구를 추가했습니다.
- 원격 저장소 기준 clone/pull 실습을 위해 2026-04-03에 복제본 변경 후 pull 절차를 다시 확인했습니다.

## 파일 구조

주요 파일 구조는 아래와 같습니다.

```text
cs_2/
├── main.py
├── app/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── constants.py
│   ├── model/
│   │   ├── __init__.py
│   │   └── quiz.py
│   ├── service/
│   │   ├── __init__.py
│   │   └── quiz_game.py
│   ├── repository/
│   │   ├── __init__.py
│   │   └── state_repository.py
│   └── ui/
│       ├── __init__.py
│       └── console_ui.py
├── state.json
└── tests/
    ├── test_quiz.py
    ├── test_state_repository.py
    └── test_quiz_game.py
```

## 계층 구조 메모

- `app/ui`: 콘솔 입출력 처리
- `app/model`: 문제 데이터와 정답 규칙
- `app/service`: 게임 진행 흐름과 상태 관리
- `app/repository`: JSON 저장소 접근 처리
- `app/config`: 상수와 설정값 관리

## 설계 메모

- 구조는 `Layered Architecture + Application Service + Repository + UI 분리` 기준으로 정리했습니다.
- `Quiz`: 문제 데이터와 정답 판정을 담당하는 모델입니다.
- `ConsoleUI`: 콘솔 입출력과 입력값 검증을 담당합니다.
- `QuizGame`: 메뉴 흐름, 점수 계산, 보너스 기능을 조합하는 애플리케이션 서비스입니다.
- `StateRepository`: `state.json` 저장, 불러오기, 스키마 검증을 담당합니다.

## 데이터 파일 설명

- 경로: 프로젝트 루트의 `state.json`
- 역할: 퀴즈 목록, 최고 점수, 플레이 히스토리 저장
- 생성 시점: 첫 실행 후 자동 생성되거나, 손상 파일 복구 시 재생성됨
- 필수 스키마:

```json
{
  "quizzes": [
    {
      "question": "Python의 창시자는?",
      "choices": ["Guido", "Linus", "Bjarne", "James"],
      "answer": 1
    }
  ],
  "best_score": null
}
```

- 보너스 확장 스키마:

```json
{
  "quizzes": [
    {
      "question": "Python의 창시자는?",
      "choices": ["Guido", "Linus", "Bjarne", "James"],
      "answer": 1,
      "hint": "이름이 Guido로 시작합니다."
    }
  ],
  "best_score": 40,
  "history": [
    {
      "played_at": "2026-04-03T15:30:00",
      "total_questions": 5,
      "correct_count": 4,
      "score": 38,
      "hint_used_count": 1
    }
  ]
}
```
