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

## 파일 구조

```text
cs_2/
├── main.py
├── constants.py
├── quiz.py
├── console_ui.py
├── state_manager.py
├── quiz_game.py
├── state.json
└── tests/
    ├── test_quiz.py
    ├── test_state_manager.py
    └── test_quiz_game.py
```

## 데이터 파일 설명

- 경로: 프로젝트 루트의 `state.json`
- 역할: 퀴즈 목록, 최고 점수, 플레이 히스토리 저장
- 기본 스키마:

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

