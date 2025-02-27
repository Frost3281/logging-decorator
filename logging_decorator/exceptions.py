from dataclasses import dataclass


@dataclass
class WrongFunctionTypeError(Exception):
    """Неправильный тип функции."""

    should_be_async: bool

    def __str__(self) -> str:
        """Строковое представление ошибки."""
        func_type = "асинхронная" if self.should_be_async else "синхронная"
        return f'Неправильный тип функции. Должна быть {func_type}.'
