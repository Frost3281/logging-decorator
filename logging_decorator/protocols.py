from typing import Any, Protocol


class Logger(Protocol):
    """Протокол логгера."""

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Сообщение в уровне дебаг."""

    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Сообщение в уровне исключения."""
