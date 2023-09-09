from typing import Any, Iterator
from unittest.mock import patch

import pytest


class MockLogger:
    """Заглушка для логгера."""

    def __init__(self) -> None:
        self.logged_messages: list[str] = []

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logged_messages.append(msg)

    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logged_messages.append(msg)


@pytest.fixture()
def mock_logger() -> MockLogger:
    return MockLogger()


@pytest.fixture(autouse=True)
def patch_sleep() -> Iterator[None]:
    with patch("time.sleep", return_value=None):
        yield
