from typing import Any, Protocol


class Logger(Protocol):
    """Протокол логгера."""

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Сообщение в уровне инфо."""

    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Сообщение в уровне исключения."""
