import json
import os
from json import JSONDecodeError
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional, Union

import app.config.constants as constants
from app.application.state.game_snapshot import GameSnapshot
from app.repository.state_payload_mapper import StatePayloadMapper


class StateJsonLoader:
    def __init__(self, state_file: Path) -> None:
        self.state_file = state_file

    def load(self) -> object:
        state_file = self.state_file
        with state_file.open(
            constants.FILE_READ_MODE,
            encoding=constants.STATE_ENCODING,
        ) as file:
            return json.load(file)


class StateJsonWriter:
    def __init__(self, state_file: Path) -> None:
        self.state_file = state_file

    def write(self, payload: object) -> None:
        temporary_file: Path | None = None
        try:
            temporary_file = self._written_temporary_file(payload)
            self._replace_state_file(temporary_file)
        except Exception:
            self._cleanup_temporary_file(temporary_file)
            raise

    def _written_temporary_file(self, payload: object) -> Path:
        state_directory = self._state_directory()
        state_file = self.state_file
        with NamedTemporaryFile(
            mode=constants.FILE_WRITE_MODE,
            encoding=constants.STATE_ENCODING,
            dir=state_directory,
            prefix=f".{state_file.name}.",
            suffix=".tmp",
            delete=False,
        ) as file:
            temporary_file = Path(file.name)
            json.dump(
                payload,
                file,
                ensure_ascii=constants.STATE_JSON_ENSURE_ASCII,
                indent=constants.STATE_JSON_INDENT,
            )
            file.flush()
            os.fsync(file.fileno())
        return temporary_file

    def _replace_state_file(self, temporary_file: Path) -> None:
        temporary_file.replace(self.state_file)

    def _state_directory(self) -> Path:
        state_directory = self.state_file.parent
        state_directory.mkdir(parents=True, exist_ok=True)
        return state_directory

    def _cleanup_temporary_file(self, temporary_file: Path | None) -> None:
        if temporary_file is None:
            return
        try:
            temporary_file.unlink()
        except FileNotFoundError:
            return
        except OSError:
            return


class StateFileBackup:
    def __init__(self, state_file: Path) -> None:
        self.state_file = state_file

    def backup_existing_file(self) -> Path | None:
        state_file = self.state_file
        if not state_file.exists():
            return None
        backup_file = self._available_backup_file_path()
        state_file.replace(backup_file)
        return backup_file

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
    def load_state(self) -> GameSnapshot:
        state_json_loader = StateJsonLoader(self.state_file)
        try:
            payload_source = state_json_loader.load()
        except FileNotFoundError:
            raise
        except JSONDecodeError as decode_error:
            raise ValueError(constants.ERROR_INVALID_JSON_STATE) from decode_error
        except OSError:
            raise
        return self._validated_state(payload_source)

    # 현재 게임 상태를 JSON 파일로 저장합니다.
    def save_state(
        self,
        game_snapshot: GameSnapshot,
    ) -> None:
        payload_mapper = self.payload_mapper
        state_payload = payload_mapper.to_state_payload(game_snapshot)
        payload = payload_mapper._payload_dictionary(state_payload)
        state_json_writer = StateJsonWriter(self.state_file)
        state_json_writer.write(payload)

    def backup_state_file(self) -> Path | None:
        state_file_backup = StateFileBackup(self.state_file)
        return state_file_backup.backup_existing_file()

    def _validated_state(self, payload_source: object) -> GameSnapshot:
        payload_mapper = self.payload_mapper
        try:
            state_payload = payload_mapper._state_payload(payload_source)
            return payload_mapper.from_state_payload(state_payload)
        except ValueError as validation_error:
            raise ValueError(constants.ERROR_INVALID_STATE_SCHEMA) from validation_error
