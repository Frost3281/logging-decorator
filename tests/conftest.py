from typing import Any, Iterator
from unittest.mock import patch

import pytest


class MockLogger:
    """Заглушка логгера для тестирования."""

    def __init__(self) -> None:
        self.messages: list[dict[str, Any]] = []

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Логирование информационного сообщения."""
        self.messages.append({'level': 'INFO', 'msg': msg, **kwargs})

    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Логирование сообщения об ошибке."""
        self.messages.append({'level': 'ERROR', 'msg': msg, **kwargs})


@pytest.fixture(name='logger')
def mock_logger() -> MockLogger:
    return MockLogger()


@pytest.fixture(autouse=True)
def _patch_sleep() -> Iterator[None]:
    with patch('time.sleep', return_value=None):
        yield
