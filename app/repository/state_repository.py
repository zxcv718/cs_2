import json
import os
from json import JSONDecodeError
from pathlib import Path
from tempfile import NamedTemporaryFile
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
        try:
            data = self._loaded_json()
        except FileNotFoundError:
            raise
        except JSONDecodeError as exc:
            raise ValueError(constants.ERROR_INVALID_JSON_STATE) from exc
        except OSError:
            raise
        return self._validated_state(data)

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
        temp_file: Path | None = None
        try:
            with NamedTemporaryFile(
                mode=constants.FILE_WRITE_MODE,
                encoding=constants.STATE_ENCODING,
                dir=state_directory,
                prefix=f".{state_file.name}.",
                suffix=".tmp",
                delete=False,
            ) as file:
                temp_file = Path(file.name)
                json.dump(
                    payload,
                    file,
                    ensure_ascii=constants.STATE_JSON_ENSURE_ASCII,
                    indent=constants.STATE_JSON_INDENT,
                )
                file.flush()
                os.fsync(file.fileno())
            temp_file.replace(state_file)
        except Exception:
            self._cleanup_temporary_file(temp_file)
            raise

    def backup_state_file(self) -> Path | None:
        state_file = self.state_file
        if not state_file.exists():
            return None
        backup_file = self._available_backup_file_path()
        state_file.replace(backup_file)
        return backup_file

    def _loaded_json(self) -> Any:
        state_file = self.state_file
        with state_file.open(
            constants.FILE_READ_MODE,
            encoding=constants.STATE_ENCODING,
        ) as file:
            return json.load(file)

    def _validated_state(self, data: Any) -> dict[str, Any]:
        payload_mapper = self.payload_mapper
        try:
            return payload_mapper.from_payload(data)
        except ValueError as exc:
            raise ValueError(constants.ERROR_INVALID_STATE_SCHEMA) from exc

    def _available_backup_file_path(self) -> Path:
        state_file = self.state_file
        backup_file = state_file.with_name(f"{state_file.name}.bak")
        suffix_index = 1
        while backup_file.exists():
            backup_file = state_file.with_name(
                f"{state_file.name}.bak.{suffix_index}"
            )
            suffix_index += 1
        return backup_file

    def _cleanup_temporary_file(self, temp_file: Path | None) -> None:
        if temp_file is None:
            return
        try:
            temp_file.unlink()
        except FileNotFoundError:
            return
        except OSError:
            return
