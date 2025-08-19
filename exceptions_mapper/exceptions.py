import inspect
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from types import FrameType
from typing import Any

from logging_decorator import LogConfig
from logging_decorator.logging_decorator.pretty_repr import pretty_repr


def _get_log_config() -> LogConfig:
    return LogConfig(
        skipped_args={'self', 'auto_capture', 'config'},
    )


@dataclass
class DetailedError(Exception):
    """Исключение с дополнительными данными."""

    message: str = ''
    details: dict[str, Any] | str = field(default_factory=dict)
    code: str = 'DETAILED_ERROR'
    timestamp: datetime = datetime.now(timezone.utc) + timedelta(hours=3)
    context: dict[str, Any] = field(default_factory=dict)
    config: LogConfig = field(default_factory=_get_log_config)

    def __post_init__(self) -> None:
        """Пост-инициализация."""
        self.message = self.message or self.__doc__ or 'Ошибка'
        self._capture_context()

    def _capture_context(self) -> None:
        """Автоматически собирает контекст выполнения."""
        frame = _find_relevant_frame()
        if not frame:
            return
        args = _get_args(frame, self.config)
        exclude = {*self.config.skipped_args, *args.keys()}
        self.context.update(
            {
                'locals': _get_locals(
                    frame,
                    config=LogConfig.from_config(self.config, skipped_args=exclude),
                ),
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


def _get_args(
    frame: FrameType,
    config: LogConfig,
) -> dict[str, Any]:
    """Получает аргументы функции с форматированием."""
    spec = inspect.getargvalues(frame)
    return {
        arg: pretty_repr(spec.locals[arg], config)
        for arg in spec.args
        if arg not in config.skipped_args
    }


def _get_locals(
    frame: FrameType,
    config: LogConfig,
) -> dict[str, Any]:
    """Безопасно получает локальные переменные."""
    return {
        k: pretty_repr(v, config)
        for k, v in frame.f_locals.items()
        if not k.startswith('__') and k not in config.skipped_args
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
