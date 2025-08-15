import inspect
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from types import FrameType
from typing import Any, Iterable


@dataclass
class DetailedError(Exception):
    """Исключение с дополнительными данными."""

    message: str = ''
    details: dict[str, Any] | str = field(default_factory=dict)
    code: str = 'DETAILED_ERROR'
    timestamp: datetime = datetime.now(timezone.utc) + timedelta(hours=3)
    context: dict[str, Any] = field(default_factory=dict)
    auto_capture: bool = True
    secure_variables: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        """Пост-инициализация."""
        self.message = self.message or self.__doc__ or 'Ошибка'
        if self.auto_capture:
            self._capture_context()

    def _capture_context(self) -> None:
        """Автоматически собирает контекст выполнения."""
        frame = _find_relevant_frame()
        if frame:
            args = _get_args(frame, self.secure_variables)
            exclude = {*self.secure_variables, *args.keys()}
            self.context.update(
                {
                    'locals': _get_locals(frame, exclude_args=exclude),
                    'args': args,
                },
            )

    def with_context(self, **context: Any) -> 'DetailedError':  # noqa: ANN401
        """Добавляет контекст к исключению."""
        self.context.update(context)
        return self

    def to_dict(self) -> dict[str, Any]:
        """Сериализация ошибки."""
        return {
            'error': {
                'message': self.message,
                'code': self.code,
                'details': self.details,
                'context': self.context,
                'timestamp': f'{self.timestamp:%Y-%m-%dT%H:%M:%S}',
            },
        }

    def __str__(self) -> str:
        """Строковое представление ошибки."""
        return str(self.to_dict())


def _get_args(frame: FrameType, exclude_args: Iterable[str]) -> dict[str, Any]:
    """Получает аргументы функции."""
    spec = inspect.getargvalues(frame)
    return {arg: spec.locals[arg] for arg in spec.args if arg not in exclude_args}


def _get_locals(
    frame: FrameType,
    exclude_args: Iterable[str],
) -> dict[str, Any]:
    """Безопасно получает локальные переменные."""
    return {
        k: v
        for k, v in frame.f_locals.items()
        if not k.startswith('__') and k not in exclude_args
    }


def _find_relevant_frame() -> FrameType:
    """Ищет фрейм, где было вызвано исключение."""
    frame = inspect.currentframe()
    while frame:
        if frame.f_code.co_filename == __file__:
            frame = frame.f_back
            continue
        return frame.f_back  # type: ignore
    msg = 'Не удалось найти нужный стек ошибки.'
    raise ValueError(msg)
