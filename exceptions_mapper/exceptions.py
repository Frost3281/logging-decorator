from datetime import datetime, timezone
from typing import Any


class DetailedError(Exception):
    """Исключенными с доп. данными."""

    message: str
    details: dict[str, Any] | str

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | str | None = None,
        *args: Any,  # noqa: ANN401
        code: str = 'UNKNOWN_ERROR',
        user_message: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Инициализация."""
        self.message = message or self.__doc__ or 'Ошибка сервиса'
        self.details = details or {}
        self.code = code
        self.user_message = user_message or self.message
        self.timestamp = datetime.now(timezone.utc)
        self.context = context or {}
        super().__init__(*args)

    def with_context(self, **context: Any) -> 'DetailedError':  # noqa: ANN401
        """Добавляет контекст к исключению."""
        self.context.update(context)
        return self

    def to_dict(self) -> dict[str, dict[str, int | str | dict[str, Any] | None]]:
        """Сериализация ошибки для передачи в API."""
        return {
            'error': {
                'message': self.message,
                'code': self.code,
                'details': self.details,
                'context': self.context,
                'timestamp': self.timestamp.isoformat(),
            },
        }

    def __str__(self) -> str:
        """Строковое представление."""
        return str(self.to_dict())
