from typing import Any, Protocol


class Logger(Protocol):
    """Протокол логгера."""

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """Сообщение в уровне инфо."""

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """Сообщение в уровне исключения."""
