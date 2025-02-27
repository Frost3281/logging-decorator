import inspect
import logging
from logging import Logger
from typing import Any, Callable

from logging_decorator.config import LogConfig
from logging_decorator.pretty_repr import pretty_repr


def get_default_logger() -> Logger:
    """Получаем дефолтный логгер."""
    logging.basicConfig(level=logging.DEBUG)
    return logging.getLogger()


def get_signature_repr(
    func: Callable[..., Any],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    config: LogConfig,
) -> str:
    """Форматирует аргументы функции в читаемый вид с переносами строк."""
    if not config.include_args:
        return ''
    try:
        sig = inspect.signature(func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        params = bound.arguments.items()
    except Exception:  # noqa: BLE001
        params = list(enumerate(args)) + list(kwargs.items())  # type: ignore
    arg_lines = []
    for name, value in params:
        if name in config.skipped_args:
            continue
        type_info = f': {type(value).__name__}' if config.show_types else ''
        value_repr = pretty_repr(value, config)
        arg_lines.append(f'{name}{type_info} = {value_repr}')
    return '\n  '.join(arg_lines) if arg_lines else ''
