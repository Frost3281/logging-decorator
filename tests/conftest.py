from typing import Any, Iterator
from unittest.mock import patch

import pytest


class MockLogger:
    """Заглушка для логгера."""

    def __init__(self) -> None:
        self.logged_messages: list[str] = []

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.logged_messages.append(msg)
        for extra_value in kwargs.get('extra', {}).values():
            self.logged_messages.append(extra_value)

    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.logged_messages.append(msg)  # noqa: ARG002
        for extra_value in kwargs.get('extra', {}).values():
            self.logged_messages.append(extra_value)


@pytest.fixture
def mock_logger() -> MockLogger:
    return MockLogger()


@pytest.fixture(autouse=True)
def _patch_sleep() -> Iterator[None]:
    with patch('time.sleep', return_value=None):
        yield
