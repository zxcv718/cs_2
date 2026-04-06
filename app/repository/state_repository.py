import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Optional, Union

import app.config.constants as constants
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
        state_file = self.state_file
        try:
            with state_file.open(
                constants.FILE_READ_MODE,
                encoding=constants.STATE_ENCODING,
            ) as file:
                data = json.load(file)
        except FileNotFoundError:
            raise
        except JSONDecodeError as exc:
            raise ValueError(constants.ERROR_INVALID_JSON_STATE) from exc
        except OSError:
            raise

        # 파일 형식이 맞는지 먼저 검사합니다.
        # JSON 문법이 맞아도 필요한 키가 빠졌을 수 있으므로
        # 파싱 성공 뒤에 한 번 더 스키마 검증을 합니다.
        try:
            payload_mapper = self.payload_mapper
            return payload_mapper.from_payload(data)
        except ValueError as exc:
            raise ValueError(constants.ERROR_INVALID_STATE_SCHEMA) from exc

    # 현재 게임 상태를 JSON 파일로 저장합니다.
    def save_state(
        self,
        quizzes: list[Quiz],
        best_score: Optional[int],
        history: Optional[list[dict[str, Any]]] = None,
    ) -> None:
        payload_mapper = self.payload_mapper
        payload = payload_mapper.to_payload(quizzes, best_score, history)

        # 폴더가 없으면 먼저 만들고 파일을 저장합니다.
        # dump는 파이썬 객체를 json형식으로 파일에 바로 저장하는 함수
        state_file = self.state_file
        state_directory = state_file.parent
        state_directory.mkdir(parents=True, exist_ok=True)
        with state_file.open(
            constants.FILE_WRITE_MODE,
            encoding=constants.STATE_ENCODING,
        ) as file:
            json.dump(
                payload,
                file,
                ensure_ascii=constants.STATE_JSON_ENSURE_ASCII,
                indent=constants.STATE_JSON_INDENT,
            )
