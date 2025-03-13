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
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """Инициализация."""
        self.message = message or self.__doc__ or 'Ошибка сервиса'
        self.details = details or {}
        super().__init__(*args, **kwargs)

    def to_dict(self) -> dict[str, dict[str, int | str | dict[str, Any] | None]]:
        """Сериализация ошибки для передачи в API."""
        return {
            'error': {
                'message': self.message,
                'details': self.details,
            },
        }

    def __str__(self) -> str:
        """Строковое представление."""
        return str(self.to_dict())
