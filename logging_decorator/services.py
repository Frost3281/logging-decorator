import inspect
import logging
from logging import Logger
from typing import Any, Callable


def get_default_logger() -> Logger:
    """Получаем дефолтный логгер."""
    logging.basicConfig(level=logging.DEBUG)
    return logging.getLogger()


def get_signature_repr(
    func: Callable[..., Any],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    max_arg_value_len: int = 30,
    *,
    pretty: bool = True,
) -> str:
    """Получаем строковое представление аргументов функции, сокращая длинные аргументы."""
    try:
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
    except Exception:  # noqa: BLE001
        params = []
    else:
        params = list(bound_args.arguments.items())

    args_repr = []
    for name, value in params + list(kwargs.items()):
        value_repr = repr(value)
        if max_arg_value_len and len(value_repr) > max_arg_value_len:
            value_repr = value_repr[: max_arg_value_len - 3] + '...'
        args_repr.append((name, value_repr))

    if pretty:
        return ',\n'.join([f'  {k} = {v}' for k, v in args_repr])
    return ', '.join([f'{k}={v}' for k, v in args_repr])
