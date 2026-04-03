import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Optional, Union

import app.config.constants as c
from app.model.quiz import Quiz
from app.repository.state_payload_mapper import StatePayloadMapper


# state.json 파일을 읽고 쓰는 저장소 클래스입니다.
class StateRepository:
    def __init__(
        self,
        state_file: Union[str, Path],
        payload_mapper: Optional[StatePayloadMapper] = None,
    ) -> None:
        # 문자열 경로가 들어와도 Path 객체로 통일합니다.
        self.state_file = Path(state_file)
        self.payload_mapper = payload_mapper or StatePayloadMapper()

    # 파일에서 게임 상태를 읽어 파이썬 객체로 바꿉니다.
    def load_state(self) -> dict[str, Any]:
        try:
            with self.state_file.open(c.FILE_READ_MODE, encoding=c.STATE_ENCODING) as file:
                data = json.load(file)
        except FileNotFoundError:
            raise
        except JSONDecodeError as exc:
            raise ValueError(c.ERROR_INVALID_JSON_STATE) from exc
        except OSError:
            raise

        # 파일 형식이 맞는지 먼저 검사합니다.
        # JSON 문법이 맞아도 필요한 키가 빠졌을 수 있으므로
        # 파싱 성공 뒤에 한 번 더 스키마 검증을 합니다.
        try:
            return self.payload_mapper.from_payload(data)
        except ValueError as exc:
            raise ValueError(c.ERROR_INVALID_STATE_SCHEMA) from exc

    # 현재 게임 상태를 JSON 파일로 저장합니다.
    def save_state(
        self,
        quizzes: list[Quiz],
        best_score: Optional[int],
        history: Optional[list[dict[str, Any]]] = None,
    ) -> None:
        payload = self.payload_mapper.to_payload(quizzes, best_score, history)

        # 폴더가 없으면 먼저 만들고 파일을 저장합니다.
        # dump는 파이썬 객체를 json형식으로 파일에 바로 저장하는 함수
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with self.state_file.open(c.FILE_WRITE_MODE, encoding=c.STATE_ENCODING) as file:
            json.dump(
                payload,
                file,
                ensure_ascii=c.STATE_JSON_ENSURE_ASCII,
                indent=c.STATE_JSON_INDENT,
            )
