from typing import Callable, Union

import app.config.constants as constants
from app.service.quiz_metrics import MenuChoice


class ConsoleInput:
    def __init__(self, error_notifier: Callable[[str], None]) -> None:
        self.error_notifier = error_notifier

    def request_menu_choice(self, min_value: int, max_value: int) -> MenuChoice:
        prompt = constants.PROMPT_MENU_CHOICE
        menu_number = self.request_valid_number(prompt, min_value, max_value)
        return MenuChoice(menu_number)

    def request_valid_number(
        self,
        prompt: str,
        min_value: int,
        max_value: int,
    ) -> int:
        while True:
            raw = input(prompt)
            validated_number = self._validated_number(raw, min_value, max_value)
            if validated_number is not None:
                return validated_number

    def request_non_empty_text(self, prompt: str) -> str:
        while True:
            raw_text = input(prompt)
            non_empty_text = self._non_empty_text(raw_text)
            if non_empty_text is not None:
                return non_empty_text

    def request_yes_no(self, prompt: str) -> bool:
        while True:
            raw_text = input(prompt)
            yes_or_no = self._yes_or_no(raw_text)
            if yes_or_no is not None:
                return yes_or_no

    def request_answer_or_hint(
        self,
        prompt: str,
        min_value: int = constants.MIN_ANSWER,
        max_value: int = constants.MAX_ANSWER,
    ) -> Union[int, str]:
        while True:
            raw_text = input(prompt)
            answer_or_hint = self._answer_or_hint(raw_text, min_value, max_value)
            if answer_or_hint is not None:
                return answer_or_hint

    def _range_error(self, min_value: int, max_value: int) -> str:
        template = constants.ERROR_RANGE_TEMPLATE
        return template.format(
            min_value=min_value,
            max_value=max_value,
        )

    def _validated_number(
        self,
        raw: str,
        min_value: int,
        max_value: int,
    ) -> int | None:
        error_notifier = self.error_notifier
        normalized = raw.strip()
        if not normalized:
            error_notifier(constants.ERROR_EMPTY_INPUT)
            return None
        return self._parsed_number(normalized, min_value, max_value)

    def _parsed_number(
        self,
        normalized: str,
        min_value: int,
        max_value: int,
    ) -> int | None:
        error_notifier = self.error_notifier
        try:
            value = int(normalized)
        except ValueError:
            error_notifier(constants.ERROR_ENTER_NUMBER)
            return None
        return self._number_in_range(value, min_value, max_value)

    def _number_in_range(
        self,
        value: int,
        min_value: int,
        max_value: int,
    ) -> int | None:
        error_notifier = self.error_notifier
        if value < min_value or value > max_value:
            range_error = self._range_error(min_value, max_value)
            error_notifier(range_error)
            return None
        return value

    def _non_empty_text(self, raw_text: str) -> str | None:
        error_notifier = self.error_notifier
        value = raw_text.strip()
        if not value:
            error_notifier(constants.ERROR_EMPTY_INPUT)
            return None
        return value

    def _yes_or_no(self, raw_text: str) -> bool | None:
        error_notifier = self.error_notifier
        normalized = raw_text.strip()
        value = normalized.lower()
        if value in constants.YES_TOKENS:
            return True
        if value in constants.NO_TOKENS:
            return False
        error_notifier(constants.ERROR_YES_NO_INPUT)
        return None

    def _answer_or_hint(
        self,
        raw_text: str,
        min_value: int,
        max_value: int,
    ) -> Union[int, str, None]:
        error_notifier = self.error_notifier
        normalized = raw_text.strip()
        value = normalized.lower()
        if not value:
            error_notifier(constants.ERROR_EMPTY_INPUT)
            return None
        if value in constants.HINT_TOKENS:
            return constants.HINT_COMMAND_VALUE
        return self._answer_number(value, min_value, max_value)

    def _answer_number(
        self,
        value: str,
        min_value: int,
        max_value: int,
    ) -> int | None:
        error_notifier = self.error_notifier
        try:
            number = int(value)
        except ValueError:
            error_notifier(constants.ERROR_ANSWER_OR_HINT_INPUT)
            return None
        return self._answer_in_range(number, min_value, max_value)

    def _answer_in_range(
        self,
        number: int,
        min_value: int,
        max_value: int,
    ) -> int | None:
        error_notifier = self.error_notifier
        if number < min_value or number > max_value:
            range_error = self._range_error(min_value, max_value)
            error_notifier(range_error)
            return None
        return number
